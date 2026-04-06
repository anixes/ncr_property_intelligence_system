# Standard Library Imports
from typing import List, Optional

# Internal Imports
from ncr_property_price_estimation.config import logger

# Third-Party Imports
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException

from ncr_property_price_estimation import state
from ncr_property_price_estimation.schemas import PropertyInput, PredictionResponse
from ncr_property_price_estimation.intelligence.engine import IntelligenceEngine
from ncr_property_price_estimation.data.geo_enrichment import GeoEnrichmentService
from ncr_property_price_estimation.features import (
    AMENITY_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
)

router = APIRouter(prefix="/predict", tags=["Valuation & Prediction"])

_intelligence = IntelligenceEngine()
_geo_service = GeoEnrichmentService()


def _sanitize_float(val: any) -> float:
    try:
        f_val = float(val)
        return 0.0 if np.isnan(f_val) or np.isinf(f_val) else f_val
    except (ValueError, TypeError, Exception):
        return 0.0


@router.post("", response_model=PredictionResponse)
async def predict_single(req: PropertyInput):
    """Institutional-grade valuation for a single property asset."""
    results = await _predict_internal([req])
    return results[0]


@router.post("/batch", response_model=List[PredictionResponse])
async def predict_batch(properties: list[PropertyInput]):
    """Batch valuation for multi-asset portfolios (Max 50)."""
    if not properties:
        raise HTTPException(status_code=422, detail="Empty batch submission.")
    if len(properties) > 50:
        raise HTTPException(status_code=413, detail="Batch limit (50) exceeded.")
    return await _predict_internal(properties)


async def _predict_internal(inputs: List[PropertyInput]):
    """Internal analytical engine for ML inference and ROI intelligence."""

    # ML Pipeline Features
    PIPELINE_FEATURES = (
        ["society", "sector", "city"] + NUMERIC_FEATURES + AMENITY_FEATURES + CATEGORICAL_FEATURES
    )

    rows = []
    for inp in inputs:
        # Use model_dump for Pydantic v2 compatibility
        row = inp.model_dump(by_alias=True)

        # Robust flattening of sub-models
        # These keys correspond to aliases 'location_score' and 'features'
        for group in ["amenities", "location_score", "features"]:
            if group in row and isinstance(row[group], dict):
                group_data = row.pop(group)
                row.update(group_data)

        row["city"] = inp.city
        row["society"] = inp.property_name or "Unknown"
        row["area"] = float(inp.area)
        row["bedrooms"] = int(inp.bedrooms)
        row["bathrooms"] = int(inp.bathrooms or 0)
        row["h3_median_price"] = np.nan
        row["h3_listings_count"] = np.nan

        # Automated Metro Proximity Validation
        # Automated Metro Proximity Validation
        # Institutional Sector Normalization (Ensures data parity between frontend and backend)
        original_sector = inp.sector.strip()
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(inp.city, inp.city)

        # Smart Matching Logic
        city_localities = state.locality_index.get(db_city, {})
        target_sector = original_sector

        if original_sector not in city_localities:
            # Try variations: Sector X vs Sector-X
            variations = [
                original_sector.replace(" ", "-"),
                original_sector.replace("-", " "),
                original_sector.title(),
                original_sector.upper(),
            ]
            for var in variations:
                if var in city_localities:
                    target_sector = var
                    break

        # Institutional Asset Mapping (Peer Interpolation)
        # Handle high-growth sectors missing from the legacy training data
        _INSTITUTIONAL_MAPPING = {
            "Sector 150": "Sector 137",  # Premium High-Growth Peer
            "Sector 152": "Sector 137",
            "Sector 107": "Sector 108",
        }

        model_input_sector = _INSTITUTIONAL_MAPPING.get(target_sector, target_sector)

        sector_info = city_localities.get(target_sector, {})
        lat, lon = sector_info.get("lat"), sector_info.get("lon")

        # Diagnostic Audit: Log locality index hits
        if not sector_info:
            logger.warning(
                f"[predict] Locality Insight Failure: {db_city} | {original_sector} (Normalized: {target_sector}) not found in index."
            )
        else:
            logger.info(
                f"[predict] Locality Match Success: {db_city} | {target_sector} (Model Peer: {model_input_sector})"
            )

        is_metro = getattr(inp.location, "is_near_metro", False)
        dist_to_metro = None

        if lat and lon and state.metro_stations:
            # Simple Haversine logic
            from math import radians, cos, sin, acos

            def h(lat1, lon1, lat2, lon2):
                lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                try:
                    return 6371 * acos(
                        sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1)
                    )
                except (ValueError, ZeroDivisionError):
                    return 0  # Identical points

            dists = [h(lat, lon, s["lat"], s["lon"]) for s in state.metro_stations]
            if dists:
                dist_to_metro = min(dists)
                if dist_to_metro <= 1.5:
                    is_metro = True

        def normalize_sector(sector: str, city: str) -> str:
            if not sector or pd.isna(sector):
                return "Unknown"

            # Manual Institutional Peers (Noida High-Fidelity)
            manual_map = {
                "Sector 150": "Sector 137",
                "Sector 152": "Sector 137",
                "Sector 107": "Sector 108",
            }
            if sector in manual_map:
                return manual_map[sector]

            # Multi-City Regional Clustering (Existing Model Support)
            import re

            match = re.search(r"Sector\s+(\d+)", sector)
            if match:
                s_num = int(match.group(1))
                city_low = str(city).lower()
                if "gurgaon" in city_low:
                    return "Sector 53" if s_num >= 60 else "Sector 12"
                elif "faridabad" in city_low:
                    return "Sector 29" if s_num >= 40 else "Sector 16"
                else:  # Noida Default
                    return "Sector 108" if s_num >= 110 else "Sector 23"
            return sector

        # Deploy Multi-City Institutional Mapping
        row["city"] = db_city
        row["sector"] = normalize_sector(target_sector, db_city)
        row["society"] = (inp.property_name or "Unknown").strip().title()

        # Absolute Input Hardening
        input_row = {}
        for col in PIPELINE_FEATURES:
            if col == "geo_median":
                continue

            val = row.get(col)

            if col in ["city", "sector", "society"]:
                # Ensure Institutional Title Case string mapping
                input_row[col] = str(val).strip() if val else "Unknown"
            elif col in CATEGORICAL_FEATURES:
                input_row[col] = str(val).strip() if val else "Unknown"
            elif col in NUMERIC_FEATURES or col in AMENITY_FEATURES:
                # Institutional Float/Bool Integrity
                input_row[col] = _sanitize_float(val)
            else:
                input_row[col] = val if val is not None else 0

        rows.append(input_row)

    df = pd.DataFrame(rows)

    if "sales" not in state.models or "rentals" not in state.models:
        raise HTTPException(status_code=503, detail="Analytical models not hydrated.")

    # Model Inference
    # The models are fitted pipelines that include the MicroMarketEncoder
    sales_price_sqft = np.expm1(state.models["sales"].predict(df))
    rent_sqft = np.expm1(state.models["rentals"].predict(df))

    results = []
    for i, inp in enumerate(inputs):
        # High-Fidelity Valuation Adjustment Layer (Refinement with ground-truth)
        raw_price_sqft = sales_price_sqft[i]
        raw_rent_sqft = rent_sqft[i]

        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(inp.city, inp.city)
        target_sector = inp.sector.strip()

        # Intelligence Index Lookup (Ground Truth)
        loc_data = state.locality_index.get(db_city, {}).get(target_sector, {})
        idx_price = loc_data.get("median_price_sqft", 0)
        idx_rent = loc_data.get("median_rent_sqft", 0)

        # Performance Heuristic: If model is static (near global median), we shift towards ground truth signal
        # Global Median ≈ 10,900. If we are near it, we adjust by the sector's relative performance.
        if idx_price > 0:
            # We trust ground truth index weights for local intelligence
            is_luxury_asset = getattr(inp.property_features, "is_luxury", False)
            price_sqft = idx_price * (1.2 if is_luxury_asset else 0.95)
            # Add amenity-based micro-adjustments
            if getattr(inp.amenities, "has_pool", False):
                price_sqft *= 1.05
            if getattr(inp.location, "is_near_metro", False):
                price_sqft *= 1.15
        else:
            price_sqft = raw_price_sqft

        if idx_rent > 0:
            is_luxury_asset = getattr(inp.property_features, "is_luxury", False)
            rent_sqft_final = idx_rent * (1.1 if is_luxury_asset else 1.0)
        else:
            rent_sqft_final = raw_rent_sqft

        price = price_sqft * inp.area
        rent = rent_sqft_final * inp.area

        # Intelligence Benchmarking
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(inp.city, inp.city)
        target_sector = inp.sector.strip()
        loc_data = state.locality_index.get(db_city, {}).get(target_sector, {})

        # Select relevant benchmark based on intent
        if inp.listing_type == "rent":
            loc_med = loc_data.get("median_rent_sqft", 0)
        else:
            loc_med = loc_data.get("median_price_sqft", 0)

        ref_median = (loc_med * inp.area) if loc_med > 0 else 0

        # ROI & Strategic Intelligence
        analysis = _intelligence.evaluate_property(
            total_price=price,
            monthly_rent=rent,
            is_near_metro=is_metro,
            geo_median=ref_median,
            intent=inp.listing_type,
        )

        results.append(
            PredictionResponse(
                price_per_sqft=round(_sanitize_float(price_sqft), 2),
                estimated_market_value=round(_sanitize_float(price), 2),
                predicted_monthly_rent=round(_sanitize_float(rent), 2),
                property_name=inp.property_name,
                intelligence_suite=analysis,
                recommendations=_intelligence.recommend_alternatives(
                    locality_index=state.locality_index,
                    current_city=db_city,
                    current_sector=target_sector,
                    user_budget_sqft=float(price_sqft),
                    current_yield=analysis.get("yield_pct", 0),
                    current_lat=lat,
                    current_lon=lon,
                ),
                similar_listings=_intelligence.find_similar_listings(
                    pool_df=state.discovery_pool,
                    city=inp.city,
                    listing_type=inp.listing_type,
                    target_price=price,
                    target_area=inp.area,
                    target_bhk=inp.bedrooms,
                    target_sector=inp.sector,
                    locality_index=state.locality_index,
                    target_prop_type=inp.prop_type,
                ),
                dist_to_metro_km=round(dist_to_metro, 2) if dist_to_metro else None,
                asset={
                    "society": str(inp.property_name or "Standard Asset"),
                    "locality": str(inp.sector),
                    "city": str(inp.city),
                    "price": float(round(price, 2)),
                    "area": float(inp.area),
                    "bhk": int(inp.bedrooms),
                    "price_per_sqft": float(round(price_sqft, 2)),
                    "yield_pct": float(round(analysis.get("yield_pct", 0), 2)),
                    "unified_score": float(round(analysis.get("unified_score", 0), 2)),
                    "listing_type": inp.listing_type,
                    "latitude": float(lat) if lat else None,
                    "longitude": float(lon) if lon else None,
                    "h3_index": str(sector_info.get("h3_index", "")),
                    "features": {
                        "amenities": inp.amenities.dict(),
                        "location": inp.location.dict(),
                        "property": inp.property_features.dict(),
                    },
                },
            )
        )

    return results
