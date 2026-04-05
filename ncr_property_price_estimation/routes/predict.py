# Standard Library Imports
import logging
from typing import List

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
from ncr_property_price_estimation.features import AMENITY_FEATURES, CATEGORICAL_FEATURES, NUMERIC_FEATURES

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
async def predict_batch(properties: List[PropertyInput]):
    """Batch valuation for multi-asset portfolios (Max 50)."""
    if not properties:
        raise HTTPException(status_code=422, detail="Empty batch submission.")
    if len(properties) > 50:
        raise HTTPException(status_code=413, detail="Batch limit (50) exceeded.")
    return await _predict_internal(properties)

async def _predict_internal(inputs: List[PropertyInput]):
    """Internal analytical engine for ML inference and ROI intelligence."""
    
    # ML Pipeline Features
    PIPELINE_FEATURES = ["society", "sector", "city"] + NUMERIC_FEATURES + AMENITY_FEATURES + CATEGORICAL_FEATURES
    
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
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(inp.city, inp.city)
        # Institutional Sector Normalization (Ensures data parity between frontend and backend)
        target_sector = inp.sector.strip()
        
        sector_info = state.locality_index.get(db_city, {}).get(target_sector, {})
        lat, lon = sector_info.get("lat"), sector_info.get("lon")
        
        # Diagnostic Audit: Log locality index hits
        if not sector_info:
            logger.warning(f"[predict] Locality Insight Failure: {db_city} | {target_sector} not found in index.")
        
        is_metro = getattr(inp.location, "is_near_metro", False)
        dist_to_metro = None
        
        if lat and lon and state.metro_stations:
            # Simple Haversine logic
            from math import radians, cos, sin, acos
            def h(lat1, lon1, lat2, lon2):
                lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                try:
                    return 6371 * acos(sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(lon2-lon1))
                except (ValueError, ZeroDivisionError):
                    return 0 # Identical points
            
            dists = [h(lat, lon, s["lat"], s["lon"]) for s in state.metro_stations]
            if dists:
                dist_to_metro = min(dists)
                if dist_to_metro <= 1.5: is_metro = True

        # Pipeline alignment
        for col in PIPELINE_FEATURES:
            if col not in row:
                row[col] = 0 if col not in CATEGORICAL_FEATURES else "Unknown"
        
        # Ensure normalized sector/city reach the ML pipeline
        row["city"] = db_city
        row["sector"] = target_sector
        
        rows.append({col: row.get(col, 0) for col in PIPELINE_FEATURES if col != "geo_median"})

    df = pd.DataFrame(rows)
    
    if "sales" not in state.models or "rentals" not in state.models:
        raise HTTPException(status_code=503, detail="Analytical models not hydrated.")

    # Model Inference
    # The models are fitted pipelines that include the MicroMarketEncoder
    sales_price_sqft = np.expm1(state.models["sales"].predict(df))
    rent_sqft = np.expm1(state.models["rentals"].predict(df))

    results = []
    for i, inp in enumerate(inputs):
        price_sqft = sales_price_sqft[i]
        price = price_sqft * inp.area
        rent = rent_sqft[i] * inp.area
        
        # Intelligence Benchmarking
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(inp.city, inp.city)
        target_sector = inp.sector.strip()
        loc_data = state.locality_index.get(db_city, {}).get(target_sector, {})
        
        # Select relevant benchmark based on intent
        if inp.listing_type == 'rent':
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
            intent=inp.listing_type
        )

        results.append(PredictionResponse(
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
                current_lon=lon
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
                target_prop_type=inp.prop_type
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
                    "property": inp.property_features.dict()
                }
            }
        ))
    
    return results
