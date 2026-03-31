"""
Yields hyper-local spatial audits (H3 Spatial Medians),
"Best Deal" discovery, and ML-driven price benchmarks.
"""

import os
from contextlib import asynccontextmanager
from typing import Any, Literal

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Ensure package imports work when running via uvicorn
# ---------------------------------------------------------------------------
from ncr_property_price_estimation.config import (
    API_HOST,
    API_PORT,
    MLFLOW_EXPERIMENT_NAME,
)
from ncr_property_price_estimation.data.geo_enrichment import GeoEnrichmentService

# Project-level imports at module load (not mid-file)
from ncr_property_price_estimation.intelligence.engine import IntelligenceEngine

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BATCH_LIMIT = 50

PIPELINE_INPUT_COLUMNS = [
    "area",
    "bedrooms",
    "bathrooms",
    "prop_type",
    "furnishing_status",
    "legal_status",
    "city",
    "sector",
    "is_rera_registered",
    "is_luxury",
    "is_gated_community",
    "is_vastu_compliant",
    "is_servant_room",
    "is_study_room",
    "is_store_room",
    "is_pooja_room",
    "has_pool",
    "has_gym",
    "has_lift",
    "is_near_metro",
    "has_power_backup",
    "is_corner_property",
    "is_park_facing",
    "no_brokerage",
    "bachelors_allowed",
    "is_standalone",
    "is_owner_listing",
]


# ---------------------------------------------------------------------------
# Pydantic schemas — strict Literal constraints for categoricals
# ---------------------------------------------------------------------------
from ncr_property_price_estimation.schemas import (
    DiscoverRequest,
    ModelInfoResponse,
    PredictionResponse,
    PropertyInput,
)

# ---------------------------------------------------------------------------
# Global state — populated during lifespan
# ---------------------------------------------------------------------------
# Global model state
_models: dict[str, Any] = {}
_model_meta: dict[str, Any] = {}
_locality_index: dict[str, Any] = {}
_discovery_pool: pd.DataFrame = pd.DataFrame()
_hotspots_cache: dict[str, list] = {"buy": [], "rent": []}
_featured_cache: dict[str, list] = {"buy": [], "rent": []}
_metro_stations: list[dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Lifespan — load model before accepting requests
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _models, _model_meta

    from ncr_property_price_estimation.modeling.model_loader import load_model
    from ncr_property_price_estimation.spatial.h3_engine import H3Engine

    # 1. Load ML Models
    for mode in ["sales", "rentals"]:
        model, meta = load_model(mode)
        if model is None:
            print(f"[CRITICAL] Could not load {mode} model!")
            continue

        _models[mode] = model
        _model_meta[mode] = meta
        print(f"[model-load] {mode.upper()} loaded from {meta['source']}")

    # 2. Load Locality Intelligence Index
    try:
        import json

        from ncr_property_price_estimation.config import DATA_DIR, logger

        index_path = DATA_DIR / "locality_intelligence_index.json"

        if index_path.exists():
            with open(index_path) as f:
                data = json.load(f)
                # Normalize city keys to match parquet convention
                _KEY_NORMALIZE = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}
                normalized = {}
                for k, v in data.items():
                    normalized[_KEY_NORMALIZE.get(k, k)] = v
                _locality_index.clear()
                _locality_index.update(normalized)
            logger.info(
                f"[model-load] Locality Intelligence Index loaded with {len(_locality_index)} cities: {list(_locality_index.keys())}"
            )
        else:
            logger.warning(
                f"[model-load] WARNING: locality_intelligence_index.json not found at {index_path.absolute()}"
            )
    except Exception as e:
        logger.error(f"[model-load] Failed to load locality index: {e}")

    # 3. Load Discovery Pool
    try:
        from ncr_property_price_estimation.config import PROJ_ROOT, logger

        s_path = PROJ_ROOT / "data" / "model" / "model_sales.parquet"
        r_path = PROJ_ROOT / "data" / "model" / "model_rentals.parquet"

        needed_cols = [
            "city",
            "sector",
            "society",
            "listing_type",
            "bedrooms",
            "bathrooms",
            "area",
            "price_per_sqft",
            "h3_res8",
            "h3_median_price",
            "h3_listings_count",
            "prop_type",
        ]

        if s_path.exists() and r_path.exists():
            s_pool = pd.read_parquet(s_path, columns=needed_cols)
            r_pool = pd.read_parquet(r_path, columns=needed_cols)
            s_pool["total_price"] = (s_pool["price_per_sqft"] * s_pool["area"]).round(0)
            r_pool["total_price"] = (r_pool["price_per_sqft"] * r_pool["area"]).round(0)
            s_pool["area"] = s_pool["area"].round(0)
            r_pool["area"] = r_pool["area"].round(0)

            s_pool.drop_duplicates(inplace=True)
            r_pool.drop_duplicates(inplace=True)

            global _discovery_pool, _hotspots_cache
            _discovery_pool = pd.concat([s_pool, r_pool], ignore_index=True)
            _discovery_pool["society"] = _discovery_pool["society"].astype(str).str.strip()

            # Locality Healer (Recover Unknown sectors from Society Names)
            def _heal_locality(row):
                curr_sector = str(row["sector"])
                if curr_sector.lower() == "unknown":
                    soci = str(row["society"])
                    db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(
                        row["city"], row["city"]
                    )
                    if soci in _locality_index.get(db_city, {}):
                        return soci
                    return f"{row['city']} (General)"
                return curr_sector

            _discovery_pool["sector"] = _discovery_pool.apply(_heal_locality, axis=1)
            _discovery_pool.drop_duplicates(
                subset=[
                    "city",
                    "sector",
                    "society",
                    "bedrooms",
                    "area",
                    "total_price",
                    "listing_type",
                ],
                inplace=True,
            )
            _discovery_pool.drop_duplicates(inplace=True)

            # H3 Coordinate Resolution (via H3Engine)
            _discovery_pool, h3_map = H3Engine.resolve_coordinates(_discovery_pool)

            # Back-fill Locality Index with H3 Coordinates
            H3Engine.backfill_locality_coordinates(_discovery_pool, _locality_index)

            # Pre-compute Hotspots and Featured Properties
            for listing_type in ["buy", "rent"]:
                _hotspots_cache[listing_type] = H3Engine.compute_hotspots(
                    _discovery_pool, h3_map, listing_type
                )
                _featured_cache[listing_type] = H3Engine.compute_featured(
                    _discovery_pool, listing_type, _locality_index
                )

            logger.info(
                f"[model-load] Discovery Pool loaded ({len(_discovery_pool)} listings). "
                f"Hotspots cached: Buy({len(_hotspots_cache['buy'])}), Rent({len(_hotspots_cache['rent'])})"
            )
        else:
            logger.warning("[model-load] Discovery Parquet files missing!")
    except Exception as e:
        logger.error(f"[model-load] Failed to load discovery pool: {e}")

    # 4. Load Metro Stations for Proximity Engine
    try:
        from ncr_property_price_estimation.config import DATA_DIR

        metro_path = DATA_DIR / "metro_stations.json"
        if metro_path.exists():
            with open(metro_path) as f:
                _metro_stations.clear()
                _metro_stations.extend(json.load(f))
            print(
                f"[model-load] Metro Proximity Engine active with {len(_metro_stations)} stations."
            )
    except Exception as e:
        print(f"[model-load] Failed to load metro stations: {e}")

    # 5. Pre-Compute Vectorized Spatial Proximity
    try:
        from ncr_property_price_estimation.config import logger

        if not _discovery_pool.empty and _metro_stations:
            import numpy as np

            logger.info(
                "[model-load] Running highly-optimized vectorized GPS distance calculation on 43,000+ records..."
            )

            metro_lats = np.array([s["lat"] for s in _metro_stations])
            metro_lons = np.array([s["lon"] for s in _metro_stations])

            prop_lats = _discovery_pool["latitude"].to_numpy(dtype=float)
            prop_lons = _discovery_pool["longitude"].to_numpy(dtype=float)

            # Handle possible NaNs in properties coordinates
            valid_mask = ~np.isnan(prop_lats) & ~np.isnan(prop_lons)

            # Broadcasting: prop_lats shape (N, 1), metro_lats shape (M,) -> (N, M)
            lat1 = np.radians(prop_lats[valid_mask, None])
            lon1 = np.radians(prop_lons[valid_mask, None])
            lat2 = np.radians(metro_lats)
            lon2 = np.radians(metro_lons)

            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
            c = 2 * np.arcsin(np.sqrt(a))
            distances_km = 6371 * c

            min_dist = np.min(distances_km, axis=1)

            # Backfill into dataframe
            _discovery_pool["gps_dist_to_metro"] = np.nan
            _discovery_pool["gps_is_near_metro"] = False

            _discovery_pool.loc[valid_mask, "gps_dist_to_metro"] = min_dist
            _discovery_pool.loc[valid_mask, "gps_is_near_metro"] = min_dist <= 1.5

            near_metro_count = int(_discovery_pool["gps_is_near_metro"].sum())
            logger.info(
                f"[model-load] Vectorized Spatial Pre-computation complete. {near_metro_count} total properties are transit-oriented."
            )

    except Exception as e:
        logger.error(f"[model-load] Failed spatial pre-computation: {e}")

    yield
    _models.clear()
    _locality_index.clear()
    _discovery_pool = pd.DataFrame()
    _metro_stations.clear()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="NCR Property Intelligence",
    description="The NCR Property Intelligence Suite leverages hyper-local spatial intelligence and machine learning to identify high-yield real estate opportunities.",
    version="stable",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — configurable via CORS_ORIGINS env var (comma-separated)
# ---------------------------------------------------------------------------
_cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Prediction helper
# ---------------------------------------------------------------------------
_intelligence = IntelligenceEngine()
_geo_service = GeoEnrichmentService()


def _sanitize_float(val: Any) -> float:
    """Ensure float is JSON compliant (No NaN or Inf)."""
    try:
        f_val = float(val)
        if np.isnan(f_val) or np.isinf(f_val):
            return 0.0
        return f_val
    except (ValueError, TypeError):
        return 0.0


async def _predict_internal(inputs: list[PropertyInput]):
    """Dual-model Prediction with ROI Intelligence."""
    from ncr_property_price_estimation.features import (
        AMENITY_FEATURES,
        CATEGORICAL_FEATURES,
        NUMERIC_FEATURES,
    )

    # ── Pure ML Inference (No Hardcoding) ────────────────────
    PIPELINE_FEATURES = (
        ["society", "sector", "city"] + NUMERIC_FEATURES + AMENITY_FEATURES + CATEGORICAL_FEATURES
    )

    rows = []
    for inp in inputs:
        # Create a flat dictionary for the pipeline while maintaining the grouped API
        row = inp.dict(by_alias=True)

        # Flatten grouped fields for ML Pipeline (Strictly Internal)
        for group in ["amenities", "location_score", "features"]:
            if group in row and isinstance(row[group], dict):
                group_data = row.pop(group)
                row.update(group_data)

        # Pass through city (CityNormalizer in pipeline handles Gurugram)
        row["city"] = inp.city
        row["society"] = inp.property_name or "Unknown"

        # Explicit numeric coercion for safety
        row["area"] = float(inp.area)
        row["bedrooms"] = int(inp.bedrooms)
        row["bathrooms"] = int(inp.bathrooms or 0)

        row["h3_median_price"] = np.nan
        row["h3_listings_count"] = np.nan

        # Extract metadata for Intelligence Engines
        is_metro_input = getattr(inp.location, "is_near_metro", False)

        # ── Automated Metro Proximity Engine ───────────────────
        # Use sector-level coordinates to verify metro access
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(inp.city, inp.city)
        sector_info = _locality_index.get(db_city, {}).get(inp.sector, {})
        lat, lon = sector_info.get("lat"), sector_info.get("lon")

        is_metro = is_metro_input
        dist_to_metro = None

        if lat and lon and _metro_stations:
            # Simple Haversine (Vectorized-ish via min)
            from math import asin, cos, radians, sin, sqrt

            def haversine(la1, lo1, la2, lo2):
                la1, lo1, la2, lo2 = map(radians, [la1, lo1, la2, lo2])
                dlo = lo2 - lo1
                dla = la2 - la1
                a = sin(dla / 2) ** 2 + cos(la1) * cos(la2) * sin(dlo / 2) ** 2
                return 2 * asin(sqrt(a)) * 6371  # KM

            distances = [haversine(lat, lon, s["lat"], s["lon"]) for s in _metro_stations]
            if distances:
                dist_to_metro = min(distances)
                # Auto-threshold: 1.5km is generally considered 'near' in NCR
                if dist_to_metro <= 1.5:
                    is_metro = True

        # ── Inference Schema Healer ──────────────────────────────
        for col in PIPELINE_FEATURES:
            if col not in row and col != "geo_median":
                row[col] = 0 if col not in CATEGORICAL_FEATURES else "Unknown"

        ordered_row = {col: row.get(col, 0) for col in PIPELINE_FEATURES if col != "geo_median"}
        rows.append(ordered_row)

    df = pd.DataFrame(rows)

    # 1. SALES PREDICTION (Batch)
    sales_price_sqft = np.expm1(_models["sales"].predict(df))

    # 2. RENTALS PREDICTION (Batch)
    rent_sqft = np.expm1(_models["rentals"].predict(df))

    results = []
    for i, inp in enumerate(inputs):
        # ── Pure ML Discovery
        price_sqft = sales_price_sqft[i]

        # ML Model Logic for "Any"
        # Since the model needs a categorical input, we default to "Apartment" for weight calculation
        actual_prop_type = inp.prop_type
        if actual_prop_type == "Any":
            actual_prop_type = "Apartment"
        # ── Pure ML Discovery
        price_sqft = sales_price_sqft[i]

        # Localized reference for ROI analysis only
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(inp.city, inp.city)
        localized_median = (
            _locality_index.get(db_city, {}).get(inp.sector, {}).get("median_price_sqft", 0)
        )

        # Calculate totals
        price = price_sqft * inp.area
        rent = rent_sqft[i] * inp.area

        # Resolve Geo-Median for risk scoring
        # localized_median is price_per_sqft → convert to total price for comparison
        ref_median = (localized_median * inp.area) if localized_median > 0 else 0

        # Intelligence Analysis (typed scalar API — no dict key ambiguity)
        analysis = _intelligence.evaluate_property(
            total_price=price,
            monthly_rent=rent,
            is_near_metro=is_metro,
            geo_median=ref_median,
        )

        # Generate Alternatives (V2: Proximity Distance Aware)
        current_loc = _locality_index.get(db_city, {}).get(inp.sector, {})
        alternatives = _intelligence.recommend_alternatives(
            locality_index=_locality_index,
            current_city=db_city,
            current_sector=inp.sector,
            user_budget_sqft=float(sales_price_sqft[i]),
            current_yield=analysis.get("yield_pct", 0),
            current_lat=current_loc.get("lat"),
            current_lon=current_loc.get("lon"),
        )

        # Generate Discovery Matches
        listing_matches = _intelligence.find_similar_listings(
            pool_df=_discovery_pool,
            city=inp.city,
            listing_type=inp.listing_type,
            target_price=price,
            target_area=inp.area,
            target_bhk=inp.bedrooms,
            target_sector=inp.sector,
            locality_index=_locality_index,
            target_prop_type=inp.prop_type,
        )

        # ── 4. Build sanitized response ──────────────────────────────────
        results.append(
            PredictionResponse(
                price_per_sqft=round(_sanitize_float(price_sqft), 2),
                estimated_market_value=round(_sanitize_float(price), 2),
                predicted_monthly_rent=round(_sanitize_float(rent), 2),
                property_name=inp.property_name,
                intelligence_suite=analysis,
                recommendations=alternatives,
                similar_listings=listing_matches,
            )
        )

    return results


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    """API welcome message."""
    return {"message": "NCR Property Price API"}


@app.get("/health")
def health(response: Response):
    """Liveness check with model status."""
    if _discovery_pool.empty:
        response.status_code = 503

    return {
        "status": "healthy" if not _discovery_pool.empty else "degraded",
        "sales_loaded": "sales" in _models,
        "rentals_loaded": "rentals" in _models,
        "discovery_size": len(_discovery_pool) if not _discovery_pool.empty else 0,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(req: PropertyInput):
    """Predict price per sqft for a single property."""
    if not _models:
        raise HTTPException(status_code=503, detail="No models loaded")

    results = await predict_batch([req])
    return results[0]


@app.post("/predict/batch", response_model=list[PredictionResponse])
async def predict_batch(properties: list[PropertyInput]):
    """Predict price per sqft for multiple properties (max 50)."""
    if not _models:
        raise HTTPException(status_code=503, detail="No models loaded")

    if len(properties) == 0:
        raise HTTPException(status_code=422, detail="Empty batch")

    if len(properties) > BATCH_LIMIT:
        raise HTTPException(
            status_code=413,
            detail=f"Batch size {len(properties)} exceeds limit of {BATCH_LIMIT}",
        )

    return await _predict_internal(properties)


@app.post("/discover")
def discover(req: DiscoverRequest):
    """Discover real properties based on criteria."""
    if _discovery_pool.empty:
        raise HTTPException(status_code=503, detail="Discovery pool not loaded")

    results = _intelligence.discover_properties(
        pool_df=_discovery_pool,
        locality_index=_locality_index,
        req=req,
    )
    return {"listings": results}


@app.get("/intelligence/hotspots")
async def get_hotspots(listing_type: Literal["buy", "rent"] = "buy", city: str | None = None):
    """Fetch pre-cached H3 price density hotspots and featured properties."""
    featured = _featured_cache.get(listing_type, [])
    hotspots = _hotspots_cache.get(listing_type, [])

    if city and city != "Entire NCR":
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(city, city)
        featured = [f for f in featured if f.get("city") == db_city]
        hotspots = [h for h in hotspots if h.get("city") == db_city]

    return {
        "status": "success",
        "listing_type": listing_type,
        "hotspots": hotspots,
        "featured": featured,
    }


@app.get("/debug/model")
def debug_model():
    """Inspect all loaded model objects."""
    info = {}
    for mode, model in _models.items():
        info[mode] = {
            "type": str(type(model)),
            "meta": _model_meta.get(mode),
            "steps": [str(s) for s in model.steps] if hasattr(model, "steps") else None,
            "features": list(model.feature_names_in_)
            if hasattr(model, "feature_names_in_")
            else None,
        }
    return info


@app.get("/debug/locality")
def debug_locality():
    """Inspect the internal locality index state."""
    return {
        "is_empty": len(_locality_index) == 0,
        "cities": list(_locality_index.keys()),
        "sample_localities": {c: list(v.keys())[:5] for c, v in _locality_index.items()},
        "total_cities": len(_locality_index),
    }


@app.get("/debug/geocoder")
def debug_geocoder(mode: Literal["sales", "rentals"] = "sales"):
    """Inspect the internal state of the GeoMedianEncoder for a specific model."""
    model = _models.get(mode)
    if not model or not hasattr(model, "named_steps"):
        return {"error": f"Model {mode} not loaded or has no named_steps"}

    geo_encoder = model.named_steps.get("geo_encoder")
    if not geo_encoder:
        return {"error": "geo_encoder not found in pipeline"}

    return {
        "mode": mode,
        "global_median": geo_encoder.global_median_,
        "city_medians": geo_encoder.city_median_,
        "sample_sector_stats": geo_encoder.sector_stats_.head(10).to_dict()
        if hasattr(geo_encoder, "sector_stats_")
        else None,
    }


@app.get("/debug/pool")
def debug_pool():
    """Inspect the internal discovery pool."""
    if _discovery_pool.empty:
        return {"status": "empty", "pool_size": 0}
    return {
        "status": "loaded",
        "pool_size": len(_discovery_pool),
        "columns": list(_discovery_pool.columns),
        "sample": _discovery_pool.head(5).to_dict(orient="records"),
        "city_counts": _discovery_pool["city"].value_counts().to_dict(),
    }


@app.get("/debug/hotspots")
def debug_hotspots():
    """Inspect the internal hotspots cache."""
    return {
        "buy_count": len(_hotspots_cache.get("buy", [])),
        "rent_count": len(_hotspots_cache.get("rent", [])),
        "sample_buy": _hotspots_cache.get("buy", [])[:3],
        "metro_stations_count": len(_metro_stations),
    }


@app.get("/debug/fs")
def debug_fs():
    """List filesystem contents for data directory debug."""
    import os

    from ncr_property_price_estimation.config import DATA_DIR, PROJ_ROOT

    try:
        data_model = os.listdir(PROJ_ROOT / "data" / "model")
    except Exception as e:
        data_model = str(e)

    try:
        data_root = os.listdir(PROJ_ROOT / "data")
    except Exception as e:
        data_root = str(e)

    return {
        "proj_root": str(PROJ_ROOT),
        "data_dir": str(DATA_DIR),
        "data_contents": data_root,
        "model_contents": data_model,
        "cwd": os.getcwd(),
    }


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    """Return current model metadata."""
    return ModelInfoResponse(
        sales_version=_model_meta.get("sales", {}).get("version"),
        rentals_version=_model_meta.get("rentals", {}).get("version"),
        experiment_name=MLFLOW_EXPERIMENT_NAME,
    )


@app.get("/debug/files")
def debug_files():
    import os
    import traceback

    from ncr_property_price_estimation.config import PROJ_ROOT

    data_model = PROJ_ROOT / "data" / "model"
    files = []
    if data_model.exists():
        files = os.listdir(data_model)

    read_error = None
    s_path = data_model / "model_sales.parquet"
    if s_path.exists():
        import pandas as pd

        try:
            needed_cols = [
                "city",
                "sector",
                "society",
                "bedrooms",
                "area",
                "price_per_sqft",
                "h3_res8",
                "h3_median_price",
                "h3_listings_count",
                "prop_type",
            ]
            pd.read_parquet(s_path, columns=needed_cols)
        except Exception:
            read_error = traceback.format_exc()

    return {
        "exists": data_model.exists(),
        "files": files,
        "read_error": read_error,
        "s_path_size": s_path.stat().st_size if s_path.exists() else 0,
    }


@app.get("/locality/list")
def locality_list(city: str):
    """Return sorted list of localities for a given city."""
    city_data = _locality_index.get(city, {})
    return {"city": city, "localities": sorted(list(city_data.keys()))}


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "ncr_property_price_estimation.api:app",
        host=API_HOST,
        port=API_PORT,
    )
