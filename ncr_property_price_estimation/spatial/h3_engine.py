"""
Spatial Intelligence Engine — H3 Hexagonal Market Analysis.

Centralizes all H3-based coordinate resolution, hotspot aggregation,
and featured property pre-computation.
"""

from typing import Any

import h3
import pandas as pd

from ncr_property_price_estimation.intelligence.risk_engine import RiskEngine
from ncr_property_price_estimation.intelligence.roi_engine import ROIEngine
from ncr_property_price_estimation.intelligence.scoring_engine import ScoringEngine


class H3Engine:
    """Centralized H3 spatial intelligence engine."""

    @staticmethod
    def resolve_coordinates(pool_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        Add latitude/longitude columns to pool_df from H3 hex indices.

        Returns:
            (pool_df_with_coords, h3_map) where h3_map is {h3_index: {lat, lng}}
        """
        if "h3_res8" not in pool_df.columns:
            return pool_df, {}

        unique_h3 = pool_df["h3_res8"].unique()
        h3_map: dict[str, dict[str, float | None]] = {}

        for h in unique_h3:
            try:
                lat, lng = h3.cell_to_latlng(h)
                h3_map[h] = {"latitude": lat, "longitude": lng}
            except Exception:
                h3_map[h] = {"latitude": None, "longitude": None}

        pool_df["latitude"] = pool_df["h3_res8"].map(lambda x: h3_map[x]["latitude"])
        pool_df["longitude"] = pool_df["h3_res8"].map(lambda x: h3_map[x]["longitude"])

        return pool_df, h3_map

    @staticmethod
    def backfill_locality_coordinates(
        pool_df: pd.DataFrame, locality_index: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Back-fill locality index with H3-derived coordinates for sectors
        that don't have lat/lon yet.
        """
        for _, row in pool_df.iterrows():
            c, s = row["city"], row["sector"]
            if c in locality_index and s in locality_index[c]:
                if "lat" not in locality_index[c][s]:
                    locality_index[c][s]["lat"] = row.get("latitude")
                    locality_index[c][s]["lon"] = row.get("longitude")
        return locality_index

    @staticmethod
    def compute_hotspots(
        pool_df: pd.DataFrame,
        h3_map: dict,
        listing_type: str,
    ) -> list[dict[str, Any]]:
        """
        Compute H3 hexagon-level market hotspots for heatmap visualization.

        Each hotspot record contains:
            h3_index, latitude, longitude, median_price_sqft, density, city
        """
        sub_df = pool_df[pool_df["listing_type"].str.lower() == listing_type].copy()
        if sub_df.empty:
            return []

        h3_agg = (
            sub_df.groupby(["h3_res8", "city"])
            .agg(
                median_price_sqft=("price_per_sqft", "median"),
                density=("price_per_sqft", "count"),
            )
            .reset_index()
        )

        h3_agg["latitude"] = h3_agg["h3_res8"].map(lambda x: h3_map.get(x, {}).get("latitude"))
        h3_agg["longitude"] = h3_agg["h3_res8"].map(lambda x: h3_map.get(x, {}).get("longitude"))

        return h3_agg.dropna(subset=["latitude"]).to_dict(orient="records")

    @staticmethod
    def compute_featured(
        pool_df: pd.DataFrame,
        listing_type: str,
        locality_index: dict[str, Any] | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Surface top featured properties for the Discovery Engine.

        Computes real unified_score and yield_pct instead of using hardcoded defaults.
        """
        sub_df = pool_df[pool_df["listing_type"].str.lower() == listing_type].copy()
        if sub_df.empty:
            return []

        # Quality filter: must have valid price and named society
        mask = (
            (sub_df["total_price"] > 0)
            & (sub_df["society"].notna())
            & (sub_df["society"].astype(str).str.lower() != "unknown")
            & (~sub_df["society"].astype(str).str.contains("Unknown", case=False))
        )

        featured = sub_df[mask].sort_values("total_price", ascending=False).head(limit)
        featured_list = []

        for _, row in featured.iterrows():
            area = float(row.get("area", 0)) if pd.notna(row.get("area")) else 0.0
            price = float(row.get("total_price", 0)) if pd.notna(row.get("total_price")) else 0.0
            price_sqft = (
                float(row.get("price_per_sqft", 0)) if pd.notna(row.get("price_per_sqft")) else 0.0
            )

            if price <= 0 or area <= 0:
                continue

            # Compute real yield and score
            city = str(row["city"])
            sector = str(row["sector"])

            # Approximate rent for yield calculation
            geo_rent_sqft = 0.0
            if locality_index:
                loc_data = locality_index.get(city, {}).get(sector, {})
                geo_rent_sqft = loc_data.get("median_rent_sqft", 0)

            if listing_type == "buy":
                monthly_rent = (geo_rent_sqft * area) if geo_rent_sqft > 0 else (price * 0.03 / 12)
                y_pct = ROIEngine.calculate_yield(price, monthly_rent)
            else:
                monthly_rent = price
                estimated_capital = (
                    (geo_rent_sqft * area * 12 / 0.03)
                    if geo_rent_sqft > 0
                    else (monthly_rent * 12 / 0.03)
                )
                y_pct = ROIEngine.calculate_yield(estimated_capital, monthly_rent)

            # Compute overvaluation from H3 median
            h3_med_raw = row.get("h3_median_price", 0)
            h3_med = float(h3_med_raw) if pd.notna(h3_med_raw) else 0.0
            benchmark = h3_med / area if (h3_med > 0 and area > 0) else 0.0
            overval = (price_sqft - benchmark) / (benchmark + 1e-9) * 100 if benchmark > 0 else 0

            risk_info = RiskEngine.calculate_risk_score(price, h3_med if h3_med > 0 else 0)
            normalized_risk = risk_info["score"] / 10.0

            unified_score = ScoringEngine.calculate_unified_score(
                yield_pct=y_pct,
                overvaluation_pct=overval,
                is_near_metro=False,
                risk_index=normalized_risk,
            )

            featured_list.append(
                {
                    "society": str(row["society"]),
                    "locality": sector,
                    "city": city,
                    "price": price,
                    "area": area,
                    "price_per_sqft": round(price_sqft, 0),
                    "yield_pct": round(y_pct, 2),
                    "unified_score": unified_score,
                    "listing_type": listing_type,
                    "bhk": int(row.get("bedrooms", 3)),
                }
            )

        return featured_list
