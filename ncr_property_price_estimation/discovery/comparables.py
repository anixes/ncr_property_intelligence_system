import re
from typing import Any

import pandas as pd

from ncr_property_price_estimation.intelligence.risk_engine import RiskEngine
from ncr_property_price_estimation.intelligence.roi_engine import ROIEngine
from ncr_property_price_estimation.intelligence.scoring_engine import ScoringEngine


class ComparablesEngine:
    @staticmethod
    def find_similar_listings(
        pool_df: pd.DataFrame,
        city: str,
        listing_type: str,
        target_price: float,
        target_area: float,
        target_bhk: int,
        locality_index: dict[str, Any],
        target_sector: str = "",
        target_prop_type: str = "Any",
    ) -> list[dict[str, Any]]:
        """
        Discover Top 5 real-world historical listings matching the search criteria.
        Includes actualized ROI metrics for each comparable.
        """
        if pool_df.empty:
            return []

        # 1. Broad Filter (City + Listing Type)
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(city, city)
        mask = (pool_df["city"] == db_city) & (
            pool_df["listing_type"].str.lower() == listing_type.lower()
        )

        # 1.5 Property Type Filter (with 'Any' bypass)
        if target_prop_type and target_prop_type != "Any":
            mask = mask & (pool_df["prop_type"] == target_prop_type)
        df = pool_df[mask].copy()

        if df.empty:
            return []

        # 2. BHK Matching (Exact if possible, then +/- 1)
        bhk_mask = df["bedrooms"] == target_bhk
        if bhk_mask.sum() < 5:
            bhk_mask = (df["bedrooms"] >= target_bhk - 1) & (df["bedrooms"] <= target_bhk + 1)

        # 3. Price & Area Range (±30%)
        p_min, p_max = target_price * 0.7, target_price * 1.3
        a_min, a_max = target_area * 0.7, target_area * 1.3

        range_mask = (df["total_price"].between(p_min, p_max)) & (df["area"].between(a_min, a_max))

        # NEW: Prefer sector-level matches first
        matches = pd.DataFrame()
        if target_sector:
            sector_mask = df["sector"].str.lower() == target_sector.lower()
            sector_matches = df[bhk_mask & sector_mask & range_mask].copy()
            if len(sector_matches) >= 3:
                matches = sector_matches
            elif len(sector_matches) > 0:
                city_matches = df[bhk_mask & range_mask].copy()
                matches = pd.concat([sector_matches, city_matches]).drop_duplicates(
                    subset=["society", "total_price", "area"]
                )
            else:
                matches = df[bhk_mask & range_mask].copy()
        else:
            matches = df[bhk_mask & range_mask].copy()

        if matches.empty:
            matches = df[bhk_mask].head(50).copy()

        # 4. Proximity Scoring
        price_dist = (matches["total_price"] - target_price).abs() / target_price
        area_dist = (matches["area"] - target_area).abs() / target_area

        # Give a small boost to items exactly matching the sector if specified
        sector_boost = 0.0
        if target_sector and "sector" in matches.columns:
            sector_boost = (matches["sector"].str.lower() == target_sector.lower()).astype(
                float
            ) * 0.1

        matches["similarity_score"] = 1.0 - (price_dist * 0.5 + area_dist * 0.5) + sector_boost

        # 5. Format & Enrich
        top_matches = matches.sort_values("similarity_score", ascending=False).head(5)

        results = []
        for _, row in top_matches.iterrows():
            area = round(float(row.get("area", 0)), 0) if pd.notna(row.get("area")) else 0.0
            price = (
                round(float(row.get("total_price", 0)), 0)
                if pd.notna(row.get("total_price"))
                else 0.0
            )
            price_sqft = (
                float(row.get("price_per_sqft", 0)) if pd.notna(row.get("price_per_sqft")) else 0.0
            )

            # Strict Filter
            if price <= 0 or area <= 0:
                continue

            # Normalized Yield & ROI for Comparables
            # If the row is from a Sales dataset, it won't have predicted_monthly_rent.
            # We must estimate it using the Locality Intelligence Index.
            rent = float(row.get("predicted_monthly_rent", 0))
            if rent <= 0:
                loc_data = locality_index.get(db_city, {}).get(row["sector"], {})
                rent_sqft = loc_data.get("median_rent_sqft", 0)
                if rent_sqft > 0:
                    rent = rent_sqft * area
                else:
                    # Generic fallback: 3% annual yield
                    rent = (price * 0.03) / 12

            y_pct = ROIEngine.calculate_yield(price, rent)

            h3_med_raw = row.get("h3_median_price", 0)
            h3_med = float(h3_med_raw) if pd.notna(h3_med_raw) else 0.0

            overval = (price_sqft - h3_med) / h3_med * 100 if h3_med > 0 else 0
            risk_info = RiskEngine.calculate_risk_score(price, h3_med * area if h3_med > 0 else 0)

            # Normalize risk from 0–100 to 0–10 for scoring engine
            normalized_risk = risk_info["score"] / 10.0

            listing_score = ScoringEngine.calculate_unified_score(
                yield_pct=y_pct,
                overvaluation_pct=overval,
                is_near_metro=False,
                risk_index=normalized_risk,
            )

            results.append(
                {
                    "society": str(row["society"]),
                    "locality": str(row["sector"]),
                    "city": city,
                    "price": price,
                    "area": area,
                    "bhk": int(row["bedrooms"]) if pd.notna(row["bedrooms"]) else 0,
                    "price_per_sqft": float(round(price_sqft, 0)),
                    "yield_pct": float(round(y_pct, 2)),
                    "unified_score": float(listing_score),
                    "listing_type": listing_type.lower(),
                    "longitude": float(row["longitude"])
                    if pd.notna(row.get("longitude"))
                    else None,
                    "latitude": float(row["latitude"]) if pd.notna(row.get("latitude")) else None,
                    "h3_index": str(row.get("h3_index", "")),
                    "features": {
                        "amenities": {
                            "has_pool": bool(row.get("has_pool", 0)),
                            "has_gym": bool(row.get("has_gym", 0)),
                            "has_lift": bool(row.get("has_lift", 0)),
                            "has_power_backup": bool(row.get("has_power_backup", 0)),
                            "is_gated_community": bool(row.get("is_gated_community", 0)),
                            "has_clubhouse": bool(row.get("has_clubhouse", 0)),
                            "has_maintenance": bool(row.get("has_maintenance", 0)),
                            "has_wifi": bool(row.get("has_wifi", 0)),
                            "is_high_ceiling": bool(row.get("is_high_ceiling", 0)),
                        },
                        "location": {
                            "is_near_metro": bool(row.get("gps_is_near_metro", 0)),
                            "is_corner_property": bool(row.get("is_corner_property", 0)),
                            "is_park_facing": bool(row.get("is_park_facing", 0)),
                            "is_vastu_compliant": bool(row.get("is_vastu_compliant", 0)),
                        },
                        "property": {
                            "is_luxury": bool(row.get("is_luxury", 0)),
                            "is_servant_room": bool(row.get("is_servant_room", 0)),
                            "is_study_room": bool(row.get("is_study_room", 0)),
                            "is_store_room": bool(row.get("is_store_room", 0)),
                            "is_pooja_room": bool(row.get("is_pooja_room", 0)),
                            "is_new_construction": bool(row.get("is_new_construction", 0)),
                        },
                    },
                }
            )

        # Alpha-Normalized Deduplication
        best_deals: dict[tuple, dict] = {}
        for res in results:
            norm_soc = re.sub(r"[^a-z0-9]", "", str(res["society"]).lower())
            key = (norm_soc, round(res.get("area", 0), 0), res.get("bhk", 0), res["listing_type"])
            if key not in best_deals or res["price"] < best_deals[key]["price"]:
                best_deals[key] = res

        return list(best_deals.values())
