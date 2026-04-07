import json
from typing import Any

import numpy as np
import pandas as pd

from ncr_property_price_estimation.config import DATA_DIR, PROJ_ROOT, logger
from ncr_property_price_estimation.spatial.h3_engine import H3Engine

# Global state containers
models: dict[str, Any] = {}
model_meta: dict[str, Any] = {}
locality_index: dict[str, Any] = {}
discovery_pool: pd.DataFrame = pd.DataFrame()
hotspots_cache: dict[str, list] = {"buy": [], "rent": []}
featured_cache: dict[str, list] = {"buy": [], "rent": []}
metro_stations: list[dict[str, Any]] = []


async def load_institutional_state():
    """Tactical hydration of the global analytical state."""
    global \
        models, \
        model_meta, \
        locality_index, \
        discovery_pool, \
        hotspots_cache, \
        featured_cache, \
        metro_stations

    from ncr_property_price_estimation.modeling.model_loader import load_model

    # 1. Load ML Models
    for mode in ["sales", "rentals"]:
        model, meta = load_model(mode)
        if model:
            models[mode] = model
            model_meta[mode] = meta
            logger.info(f"[state] {mode.upper()} model loaded from {meta['source']}")

    # 2. Load Locality Intelligence
    index_path = DATA_DIR / "locality_intelligence_index.json"
    if index_path.exists():
        with open(index_path) as f:
            data = json.load(f)
            # 2. Institutional Locality Hydration & Key-Normalization
            _RAW_NORMALIZE = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}

            l_index = {}
            for k, v in data.items():
                norm_k = _RAW_NORMALIZE.get(k, k)
                if norm_k in l_index:
                    l_index[norm_k].update(v)
                else:
                    l_index[norm_k] = v

            # 3. Heuristic Extraction (Handling Greater Noida localities nested in Ghaziabad/Noida)
            if "Greater_Noida" not in l_index:
                l_index["Greater_Noida"] = {}

            for city_key in list(l_index.keys()):
                if city_key == "Greater_Noida":
                    continue

                # Check for Greater Noida signatures in locality names
                localities = l_index[city_key]
                to_move = [loc for loc in list(localities.keys()) if "Greater Noida" in loc]

                for loc in to_move:
                    l_index["Greater_Noida"][loc] = localities.pop(loc)

            locality_index = l_index
            logger.info(
                f"Analytical index hydrated: {len(locality_index)} cities, {len(locality_index.get('Greater_Noida', {}))} Greater Noida localities consolidated."
            )

    # 3. Load Discovery Assets & Spatial Pre-computation
    s_path = PROJ_ROOT / "data" / "model" / "model_sales.parquet"
    r_path = PROJ_ROOT / "data" / "model" / "model_rentals.parquet"

    if s_path.exists() and r_path.exists():
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
            "furnishing_status",
            "legal_status",
            "is_servant_room",
            "is_study_room",
            "is_standalone",
            "is_owner_listing",
            "is_store_room",
            "is_pooja_room",
            "ready_to_move",
            "is_luxury",
            "is_gated_community",
            "is_vastu_compliant",
            "has_pool",
            "has_gym",
            "has_lift",
            "is_near_metro",
            "has_power_backup",
            "is_corner_property",
            "is_park_facing"
        ]
        s_pool = pd.read_parquet(s_path, columns=needed_cols)
        r_pool = pd.read_parquet(r_path, columns=needed_cols)

        # Hydrate calculated fields
        s_pool["total_price"] = (s_pool["price_per_sqft"] * s_pool["area"]).round(0)
        r_pool["total_price"] = (r_pool["price_per_sqft"] * r_pool["area"]).round(0)

        discovery_pool = pd.concat([s_pool, r_pool], ignore_index=True).drop_duplicates()

        # Spatial Coordination & Hotspots
        discovery_pool, h3_map = H3Engine.resolve_coordinates(discovery_pool)
        H3Engine.backfill_locality_coordinates(discovery_pool, locality_index)

        for lt in ["buy", "rent"]:
            hotspots_cache[lt] = H3Engine.compute_hotspots(discovery_pool, h3_map, lt)
            featured_cache[lt] = H3Engine.compute_featured(discovery_pool, lt, locality_index)

        logger.info(f"[state] Discovery Pool hydrated: {len(discovery_pool)} assets")

    # 4. Metro Proximity Engine
    metro_path = DATA_DIR / "metro_stations.json"
    if metro_path.exists():
        with open(metro_path) as f:
            metro_stations = json.load(f)

        if not discovery_pool.empty:
            _run_vectorized_metro_sync()
        logger.info(f"[state] Metro Engine active: {len(metro_stations)} stations")


def _run_vectorized_metro_sync():
    """Vectorized Haversine sync for 43,000+ assets."""
    global discovery_pool, metro_stations

    metro_lats = np.array([s["lat"] for s in metro_stations])
    metro_lons = np.array([s["lon"] for s in metro_stations])

    prop_lats = discovery_pool["latitude"].to_numpy(dtype=float)
    prop_lons = discovery_pool["longitude"].to_numpy(dtype=float)

    mask = ~np.isnan(prop_lats) & ~np.isnan(prop_lons)

    lat1, lon1 = np.radians(prop_lats[mask, None]), np.radians(prop_lons[mask, None])
    lat2, lon2 = np.radians(metro_lats), np.radians(metro_lons)

    d = (
        6371
        * 2
        * np.arcsin(
            np.sqrt(
                np.sin((lat2 - lat1) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
            )
        )
    )

    min_dist = np.min(d, axis=1)
    discovery_pool["gps_dist_to_metro"] = np.nan
    discovery_pool["gps_is_near_metro"] = False
    discovery_pool.loc[mask, "gps_dist_to_metro"] = min_dist
    discovery_pool.loc[mask, "gps_is_near_metro"] = min_dist <= 1.5


def clear_state():
    """Clinical teardown of the institutional state."""
    global models, model_meta, locality_index, discovery_pool, metro_stations
    models.clear()
    locality_index.clear()
    discovery_pool = pd.DataFrame()
    metro_stations.clear()
