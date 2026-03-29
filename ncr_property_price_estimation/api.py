"""
Yields hyper-local spatial audits (H3 Spatial Medians), 
"Best Deal" discovery, and ML-driven price benchmarks.
"""

import os
from contextlib import asynccontextmanager
from typing import Literal, Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Project-level imports at module load (not mid-file)
from ncr_property_price_estimation.intelligence.engine import IntelligenceEngine
from ncr_property_price_estimation.data.geo_enrichment import GeoEnrichmentService

# ---------------------------------------------------------------------------
# Ensure package imports work when running via uvicorn
# ---------------------------------------------------------------------------
from ncr_property_price_estimation.config import (
    API_HOST,
    API_PORT,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_MODEL_NAME,
    MLFLOW_TRACKING_URI,
    MODELS_DIR,
)

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
class PropertyInput(BaseModel):
    """Input schema for a single property prediction."""

    area: float = Field(..., gt=0, description="Built-up area in sqft")
    bedrooms: int = Field(..., ge=1, description="Number of bedrooms")
    bathrooms: int | None = Field(None, ge=0, description="Number of bathrooms")

    prop_type: Literal["Apartment", "Builder Floor", "Independent House"] = Field(
        ..., description="Property type"
    )
    furnishing_status: Literal["Fully-Furnished", "Semi-Furnished", "Unfurnished", "Unknown"] = Field(
        "Semi-Furnished", description="Furnishing status"
    )
    legal_status: Literal["Freehold", "Leasehold", "Power of Attorney", "Unknown"] = Field(
        "Unknown", description="Legal ownership status"
    )

    city: str = Field(..., description="NCR City (e.g., Gurgaon, Noida)")
    sector: str = Field(..., description="Sector or Locality Name")
    property_name: str | None = Field(None, description="Optional Project or Apartment name")

    # High-Performance Binary Catalyst Flags
    is_rera_registered: bool = False
    is_luxury: bool = False
    is_gated_community: bool = False
    is_vastu_compliant: bool = False
    is_servant_room: bool = False
    is_study_room: bool = False
    is_store_room: bool = False
    is_pooja_room: bool = False
    has_pool: bool = False
    has_gym: bool = False
    has_lift: bool = False
    is_near_metro: bool = False
    has_power_backup: bool = False
    is_corner_property: bool = False
    is_park_facing: bool = False
    no_brokerage: bool = False
    bachelors_allowed: bool = False
    is_standalone: bool = False
    is_owner_listing: bool = False


class PredictionResponse(BaseModel):
    """Output schema for a single prediction."""

    price_per_sqft: float = Field(..., description="Predicted price in ₹/sqft")
    estimated_market_value: float = Field(
        ..., description="Estimated total price (price_per_sqft × area)"
    )
    predicted_monthly_rent: float = Field(..., description="Predicted monthly rent")
    property_name: str | None = Field(None, description="Project or Property name provided")
    intelligence_suite: dict[str, Any] = Field(..., description="ROI Intelligence analysis")
    recommendations: list[dict[str, Any]] = Field(default_factory=list, description="Top 5 alternative localities")
    similar_listings: list[dict[str, Any]] = Field(default_factory=list, description="Top 5 real-world historical matches")


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_stage: str | None = None


class DiscoverRequest(BaseModel):
    city: str
    listing_type: Literal["buy", "rent"]
    bhk: list[int]
    budget_min: float
    budget_max: float
    area_min: float | None = None
    area_max: float | None = None
    sort_by: Literal["yield", "price_low", "price_high", "roi", "area"] = "yield"



class ModelInfoResponse(BaseModel):
    sales_version: str | None = None
    rentals_version: str | None = None
    experiment_name: str


# ---------------------------------------------------------------------------
# Global state — populated during lifespan
# ---------------------------------------------------------------------------
# Global model state
_models: dict[str, Any] = {}
_model_meta: dict[str, Any] = {}
_locality_index: dict[str, Any] = {}
_discovery_pool: pd.DataFrame = pd.DataFrame()
_hotspots_cache: dict[str, list] = {"buy": [], "rent": []}


# ---------------------------------------------------------------------------
# Model loading helpers
# ---------------------------------------------------------------------------
def _try_mlflow_load(mode: str):
    """Attempt to load a model from MLflow registry (Staging stage)."""
    try:
        import mlflow
        import mlflow.sklearn

        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

        # We look for staging models
        model_name = f"{MLFLOW_MODEL_NAME}_{mode}"
        model_uri = f"models:/{model_name}/Staging"
        model = mlflow.sklearn.load_model(model_uri)

        client = mlflow.tracking.MlflowClient()
        version = None
        try:
            versions = client.get_latest_versions(model_name, stages=["Staging"])
            if versions:
                version = versions[0].version
        except Exception:
            pass

        return model, {"version": version, "source": f"mlflow_registry_{mode}"}
    except Exception as exc:
        print(f"[model-load] Failed for {mode}: {exc}")
        return None, None

def _try_joblib_load(mode: str):
    """Fallback to local joblib."""
    path = MODELS_DIR / mode / f"pipeline_{mode}.joblib"
    if not path.exists():
        return None, None
    try:
        import joblib
        model = joblib.load(path)
        return model, {"version": "local", "source": str(path)}
    except Exception as e:
        print(f"[joblib] Failed to load {mode}: {e}")
        return None, None


# ---------------------------------------------------------------------------
# Lifespan — load model before accepting requests
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _models, _model_meta
    
    for mode in ["sales", "rentals"]:
        model, meta = _try_mlflow_load(mode)
        if model is None:
            model, meta = _try_joblib_load(mode)
        
        if model is None:
            print(f"[CRITICAL] Could not load {mode} model!")
            continue # Try next or raise? 
            
        _models[mode] = model
        _model_meta[mode] = meta
        print(f"[model-load] {mode.upper()} loaded from {meta['source']}")

    # Load Locality Intelligence Index
    try:
        import json
        from ncr_property_price_estimation.config import PROJ_ROOT, DATA_DIR, logger
        index_path = DATA_DIR / "locality_intelligence_index.json"
        
        if index_path.exists():
            with open(index_path, "r") as f:
                data = json.load(f)
                _locality_index.clear()
                _locality_index.update(data)
            logger.info(f"[model-load] Locality Intelligence Index loaded with {len(_locality_index)} cities from {index_path}")
        else:
            logger.warning(f"[model-load] WARNING: locality_intelligence_index.json not found at {index_path.absolute()}")
    except Exception as e:
        logger.error(f"[model-load] Failed to load locality index: {e}")

    # Load Discovery Pool
    try:
        from ncr_property_price_estimation.config import PROJ_ROOT
        s_path = PROJ_ROOT / "data" / "model" / "model_sales.parquet"
        r_path = PROJ_ROOT / "data" / "model" / "model_rentals.parquet"
        
        needed_cols = [
            "city", "sector", "society", "listing_type", 
            "bedrooms", "bathrooms", "area", "price_per_sqft",
            "h3_res8", "h3_median_price", "h3_listings_count"
        ]
        
        if s_path.exists() and r_path.exists():
            s_pool = pd.read_parquet(s_path, columns=needed_cols)
            r_pool = pd.read_parquet(r_path, columns=needed_cols)
            s_pool["total_price"] = (s_pool["price_per_sqft"] * s_pool["area"]).round(0)
            r_pool["total_price"] = (r_pool["price_per_sqft"] * r_pool["area"]).round(0)
            s_pool["area"] = s_pool["area"].round(0)
            r_pool["area"] = r_pool["area"].round(0)
            
            # Pre-concat deduplication for speed
            s_pool.drop_duplicates(inplace=True)
            r_pool.drop_duplicates(inplace=True)
            
            global _discovery_pool, _hotspots_cache
            _discovery_pool = pd.concat([s_pool, r_pool], ignore_index=True)
            _discovery_pool["society"] = _discovery_pool["society"].astype(str).str.strip()
            
            # --- Locality Healer (Recover Unknown sectors from Society Names) ---
            # This handles the data quality gap in Ghaziabad by back-filling info from known indices
            def _heal_locality(row):
                curr_sector = str(row["sector"])
                if curr_sector.lower() == "unknown":
                    soci = str(row["society"])
                    db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(row["city"], row["city"])
                    # Check if society name is actually a known sector in this city
                    if soci in _locality_index.get(db_city, {}):
                        return soci
                    # Fallback to city name for broad matching
                    return f"{row['city']} (General)"
                return curr_sector

            _discovery_pool["sector"] = _discovery_pool.apply(_heal_locality, axis=1)
            
            _discovery_pool.drop_duplicates(
                subset=["city", "sector", "society", "bedrooms", "area", "total_price", "listing_type"],
                inplace=True
            )
            # Final safety pass: drop any perfectly identical rows
            _discovery_pool.drop_duplicates(inplace=True)
            
            # 2. Faster H3 coordinate resolution...
            # This is ~88x faster than per-row .apply()
            import h3
            unique_h3 = _discovery_pool["h3_res8"].unique()
            h3_map = {}
            for h in unique_h3:
                try:
                    lat, lng = h3.cell_to_latlng(h)
                    h3_map[h] = {"latitude": lat, "longitude": lng}
                except:
                    h3_map[h] = {"latitude": None, "longitude": None}
            
            _discovery_pool["latitude"] = _discovery_pool["h3_res8"].map(lambda x: h3_map[x]["latitude"])
            _discovery_pool["longitude"] = _discovery_pool["h3_res8"].map(lambda x: h3_map[x]["longitude"])

            # 3. Pre-compute Market Hotspots for Heatmap (Zero-Load Strategy)
            for listing_type in ["buy", "rent"]:
                sub_df = _discovery_pool[_discovery_pool["listing_type"].str.lower() == listing_type].copy()
                if sub_df.empty:
                    continue
                
                # Group by H3 and calculate median price + density
                hotspots = sub_df.groupby(["h3_res8", "city"]).agg(
                    median_price_sqft=("price_per_sqft", "median"),
                    density=("price_per_sqft", "count")
                ).reset_index()
                
                # Attach coordinates from our fast map
                hotspots["latitude"] = hotspots["h3_res8"].map(lambda x: h3_map[x]["latitude"])
                hotspots["longitude"] = hotspots["h3_res8"].map(lambda x: h3_map[x]["longitude"])
                
                _hotspots_cache[listing_type] = hotspots.dropna(subset=["latitude"]).to_dict(orient="records")

            logger.info(f"[model-load] Discovery Pool loaded ({len(_discovery_pool)} listings). Hotspots cached: Buy({len(_hotspots_cache['buy'])}), Rent({len(_hotspots_cache['rent'])})")
        else:
            logger.warning("[model-load] Discovery Parquet files missing!")
    except Exception as e:
        logger.error(f"[model-load] Failed to load discovery pool: {e}")

    yield
    _models.clear()
    _locality_index.clear()
    _discovery_pool = pd.DataFrame()


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
        NUMERIC_FEATURES, AMENITY_FEATURES, CATEGORICAL_FEATURES
    )
    
    # ── Pure ML Inference (No Hardcoding) ────────────────────
    PIPELINE_FEATURES = (
        ["society", "sector", "city"] + 
        NUMERIC_FEATURES + 
        AMENITY_FEATURES + 
        CATEGORICAL_FEATURES
    )

    rows = []
    for inp in inputs:
        row = inp.dict()
        
        # Pass through city (CityNormalizer in pipeline handles Gurugram)
        row["city"] = inp.city
        row["society"] = inp.property_name or "Unknown"

        # Explicit numeric coercion for safety
        row["area"] = float(inp.area)
        row["bedrooms"] = int(inp.bedrooms)
        row["bathrooms"] = int(inp.bathrooms)
        
        row["h3_median_price"] = np.nan
        row["h3_listings_count"] = np.nan
        
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
        
        # Localized reference for ROI analysis only
        localized_median = _locality_index.get(inp.city, {}).get(inp.sector, {}).get("median_price_sqft", 0)
        
        # Calculate totals
        price = price_sqft * inp.area
        rent = rent_sqft[i] * inp.area
        
        # Resolve Geo-Median for risk scoring
        ref_median = localized_median if localized_median > 0 else 0

        # Intelligence Analysis (typed scalar API — no dict key ambiguity)
        analysis = _intelligence.evaluate_property(
            total_price=price,
            monthly_rent=rent,
            is_near_metro=inp.is_near_metro,
            geo_median=ref_median,
        )

        # Generate Alternatives
        alternatives = _intelligence.recommend_alternatives(
            locality_index=_locality_index,
            current_city=inp.city,
            current_sector=inp.sector,
            user_budget_sqft=float(sales_price_sqft[i]),
            current_yield=analysis.get("rental_yield_pct", 0)
        )

        # Generate Discovery Matches
        listing_matches = _intelligence.find_similar_listings(
            pool_df=_discovery_pool,
            city=inp.city,
            listing_type="buy" if inp.prop_type != "Rent" else "rent", # Map prop_type if needed
            target_price=price,
            target_area=inp.area,
            target_bhk=inp.bedrooms
        )

        # Last-Mile "Best Deal" Deduplication (Alpha-Normalized)
        import re
        best_deals = {}
        for l_match in listing_matches:
            # Alpha-only key to ignore hidden spaces/special chars
            norm_soc = re.sub(r'[^a-z0-9]', '', str(l_match["society"]).lower())
            lt = l_match.get("listing_type", "buy")
            key = (norm_soc, round(l_match.get("area", 0), 0), l_match.get("bhk", 0), lt)
            
            if key not in best_deals or l_match["price"] < best_deals[key]["price"]:
                best_deals[key] = l_match

        # ── 4. Build sanitized response ──────────────────────────────────
        results.append(
            PredictionResponse(
                price_per_sqft=round(_sanitize_float(price_sqft), 2),
                estimated_market_value=round(_sanitize_float(price), 2),
                predicted_monthly_rent=round(_sanitize_float(rent), 2),
                property_name=inp.property_name,
                intelligence_suite=analysis,
                recommendations=alternatives,
                similar_listings=list(best_deals.values())
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
def health():
    """Liveness check with model status."""
    return {
        "status": "healthy",
        "sales_loaded": "sales" in _models,
        "rentals_loaded": "rentals" in _models
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
        city=req.city,
        listing_type=req.listing_type,
        bhk_list=req.bhk,
        budget_min=req.budget_min,
        budget_max=req.budget_max,
        area_min=req.area_min,
        area_max=req.area_max,
        sort_by=req.sort_by
    )
    # Last-Mile "Best Deal" Deduplication (Alpha-Normalized)
    import re
    best_deals = {}
    for res in results:
        norm_soc = re.sub(r'[^a-z0-9]', '', str(res["society"]).lower())
        lt = res.get("listing_type", req.listing_type)
        key = (norm_soc, round(res.get("area", 0), 0), res.get("bhk", 0), lt)
        
        if key not in best_deals or res["price"] < best_deals[key]["price"]:
            best_deals[key] = res
            
    return {"listings": list(best_deals.values())}


@app.get("/intelligence/hotspots")
async def get_hotspots(listing_type: Literal["buy", "rent"] = "buy"):
    """Fetch pre-cached H3 price density hotspots."""
    return {
        "status": "success",
        "listing_type": listing_type,
        "hotspots": _hotspots_cache.get(listing_type, []),
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
            "features": list(model.feature_names_in_) if hasattr(model, "feature_names_in_") else None,
        }
    return info


@app.get("/debug/locality")
def debug_locality():
    """Inspect the internal locality index state."""
    return {
        "is_empty": len(_locality_index) == 0,
        "cities": list(_locality_index.keys()),
        "sample_localities": {c: list(v.keys())[:5] for c, v in _locality_index.items()},
        "total_cities": len(_locality_index)
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


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    """Return current model metadata."""
    return ModelInfoResponse(
        sales_version=_model_meta.get("sales", {}).get("version"),
        rentals_version=_model_meta.get("rentals", {}).get("version"),
        experiment_name=MLFLOW_EXPERIMENT_NAME,
    )


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
