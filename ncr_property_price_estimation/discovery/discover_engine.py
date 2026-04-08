import re
from typing import Any

import pandas as pd

from ncr_property_price_estimation.intelligence.risk_engine import RiskEngine
from ncr_property_price_estimation.intelligence.roi_engine import ROIEngine
from ncr_property_price_estimation.intelligence.scoring_engine import ScoringEngine
from ncr_property_price_estimation.schemas import DiscoverRequest


class DiscoverEngine:
    @staticmethod
    def discover_properties(
        pool_df: pd.DataFrame,
        locality_index: dict[str, Any],
        req: DiscoverRequest,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Discover Enriched Properties for Recommender UI.
        """
        city = req.city
        listing_type = req.listing_type
        bhk_list = req.bhk
        budget_min = req.budget_min
        budget_max = req.budget_max
        area_min = req.area_min
        area_max = req.area_max
        sort_by = req.sort_by
        amenities = req.amenities.dict() if req.amenities else None
        location_features = req.location_features.dict() if req.location_features else None
        property_features = req.property_features.dict() if req.property_features else None
        furnishing_status = req.furnishing_status
        legal_status = req.legal_status
        prop_type = req.prop_type
        ready_to_move = req.ready_to_move

        if pool_df.empty:
            return []

        # 1. Broad Filter (City + Listing Type)
        if city == "Entire NCR":
            mask = pool_df["listing_type"].str.lower() == listing_type.lower()
        else:
            db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(city, city)
            mask = (pool_df["city"] == db_city) & (
                pool_df["listing_type"].str.lower() == listing_type.lower()
            )

        # 1.5 Property Type & Sector Filter (with 'All Types' / 'Entire City' / 'Any' bypass)
        if prop_type and prop_type not in ["All Types", "Any"]:
            mask = mask & (pool_df["prop_type"] == prop_type)

        sector = req.sector
        if sector and sector not in ["Entire City", "Any"] and "sector" in pool_df.columns:
            # Normalize user input: "Sec 150" -> "Sector 150", "Sector-150" -> "Sector 150"
            norm_query = re.sub(r"sec\b", "Sector", sector, flags=re.IGNORECASE)
            norm_query = norm_query.replace("-", " ").strip()

            # Use regex with word boundaries for strict matching (e.g. "Sector 1" won't match "Sector 150")
            pattern = rf"\b{re.escape(norm_query)}\b"
            mask = mask & (
                pool_df["sector"].str.contains(pattern, case=False, na=False, regex=True)
            )

        # 2. BHK Matching
        if bhk_list:
            if 5 in bhk_list:
                mask = mask & ((pool_df["bedrooms"].isin(bhk_list)) | (pool_df["bedrooms"] >= 5))
            else:
                mask = mask & (pool_df["bedrooms"].isin(bhk_list))

        # 3. Budget & Area Range
        mask = mask & (pool_df["total_price"].between(budget_min, budget_max))
        if area_min:
            mask = mask & (pool_df["area"] >= area_min)
        if area_max:
            mask = mask & (pool_df["area"] <= area_max)

        # 4. Advanced Filters
        if amenities:
            for feat, val in amenities.items():
                if val and feat in pool_df.columns:
                    mask = mask & (pool_df[feat] == 1)

        if location_features:
            for feat, val in location_features.items():
                if val:
                    actual_feat = "gps_is_near_metro" if feat == "is_near_metro" else feat
                    if actual_feat in pool_df.columns:
                        mask = mask & (pool_df[actual_feat] == 1)

        if property_features:
            for feat, val in property_features.items():
                if val and feat in pool_df.columns:
                    mask = mask & (pool_df[feat] == 1)

        if (
            furnishing_status
            and furnishing_status != "Unknown"
            and "furnishing_status" in pool_df.columns
        ):
            mask = mask & (pool_df["furnishing_status"] == furnishing_status)

        if legal_status and legal_status != "Unknown" and "legal_status" in pool_df.columns:
            mask = mask & (pool_df["legal_status"] == legal_status)

        if ready_to_move is not None and "ready_to_move" in pool_df.columns:
            mask = mask & (pool_df["ready_to_move"] == (1 if ready_to_move else 0))

        df = pool_df[mask].copy()
        if df.empty:
            return []

        # Enrich with Intelligence Metrics
        results = []
        for _, row in df.iterrows():
            loc = str(row["sector"])
            area = float(row.get("area", 0)) if pd.notna(row.get("area")) else 0.0
            price = float(row.get("total_price", 0)) if pd.notna(row.get("total_price")) else 0.0
            price_sqft = (
                float(row.get("price_per_sqft", 0)) if pd.notna(row.get("price_per_sqft")) else 0.0
            )

            # Resolve normalization for the specific city of this asset
            asset_city = str(row.get("city", "Gurgaon"))
            db_city_norm = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(
                asset_city, asset_city
            )

            loc_data = locality_index.get(db_city_norm, {}).get(loc, {})
            geo_median_price_sqft = loc_data.get("median_price_sqft", 0)
            geo_median_rent_sqft = loc_data.get("median_rent_sqft", 0)

            intent = listing_type.lower()

            # Logic to approximate missing values
            if intent == "buy":
                total_price = price
                monthly_rent = (
                    (geo_median_rent_sqft * area)
                    if geo_median_rent_sqft > 0
                    else (price * 0.03 / 12)
                )
            else:
                monthly_rent = price
                total_price = (
                    (geo_median_price_sqft * area)
                    if geo_median_price_sqft > 0
                    else (monthly_rent * 12 / 0.03)
                )

            y_pct = ROIEngine.calculate_yield(total_price, monthly_rent)

            risk_target = total_price if intent == "buy" else monthly_rent
            geo_benchmark = (
                geo_median_price_sqft * area if intent == "buy" else geo_median_rent_sqft * area
            )
            risk = RiskEngine.calculate_risk_score(
                risk_target, geo_benchmark if geo_benchmark else 0, intent=intent
            )

            h3_med_raw = row.get("h3_median_price", 0)
            h3_median = float(h3_med_raw) if pd.notna(h3_med_raw) else 0.0
            h3_median_per_sqft = h3_median / area if (h3_median > 0 and area > 0) else 0.0
            benchmark = (
                h3_median_per_sqft
                if h3_median_per_sqft > 0
                else (geo_median_price_sqft if intent == "buy" else geo_median_rent_sqft)
            )
            overval = (price_sqft - benchmark) / (benchmark + 1e-9) * 100 if benchmark > 0 else 0

            # Normalize risk from 0–100 to 0–10 for scoring engine
            normalized_risk = risk["score"] / 10.0

            is_near = bool(row.get("gps_is_near_metro", False))
            unified_score = ScoringEngine.calculate_unified_score(
                yield_pct=y_pct,
                overvaluation_pct=overval,
                is_near_metro=is_near,
                risk_index=normalized_risk,
                intent=intent,
            )

            dist_val = (
                float(row.get("gps_dist_to_metro", 0.0))
                if pd.notna(row.get("gps_dist_to_metro"))
                else None
            )

            results.append(
                {
                    "society": str(row["society"]),
                    "locality": loc,
                    "city": city,
                    "price": price,
                    "area": area,
                    "bhk": int(row["bedrooms"])
                    if pd.notna(row["bedrooms"]) and row["bedrooms"] > 0
                    else (bhk_list[0] if bhk_list else 0),
                    "price_per_sqft": float(round(price_sqft, 0)),
                    "yield_pct": float(round(y_pct, 2)),
                    "unified_score": float(unified_score),
                    "risk_score": float(risk["score"]),
                    "overvaluation_pct": float(round(overval, 2)),
                    "listing_type": listing_type.lower(),
                    "latitude": float(row["latitude"]) if pd.notna(row.get("latitude")) else None,
                    "longitude": float(row["longitude"])
                    if pd.notna(row.get("longitude"))
                    else None,
                    "dist_to_metro_km": float(round(dist_val, 2)) if dist_val is not None else None,
                    "h3_index": str(row["h3_res8"])
                    if "h3_res8" in row and pd.notna(row["h3_res8"])
                    else None,
                    "furnishing_status": str(row["furnishing_status"])
                    if pd.notna(row.get("furnishing_status"))
                    and str(row.get("furnishing_status", "")).strip() not in ("", "nan", "None")
                    else "Unknown",
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
        # Key: (normalized_society, area_rounded, bhk, listing_type) → keep lowest price
        best_deals: dict[tuple, dict] = {}
        for res in results:
            norm_soc = re.sub(r"[^a-z0-9]", "", str(res["society"]).lower())
            key = (norm_soc, round(res.get("area", 0), 0), res.get("bhk", 0), res["listing_type"])
            if key not in best_deals or res["price"] < best_deals[key]["price"]:
                best_deals[key] = res

        deduped = list(best_deals.values())

        # Sorting
        if sort_by == "yield":
            deduped.sort(key=lambda x: x["yield_pct"], reverse=True)
        elif sort_by == "score":
            deduped.sort(key=lambda x: x["unified_score"], reverse=True)
        elif sort_by == "price_low":
            deduped.sort(key=lambda x: x["price"], reverse=False)
        elif sort_by == "price_high":
            deduped.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "area":
            deduped.sort(key=lambda x: x["area"], reverse=True)
        elif sort_by == "price_sqft":
            # Treat 0.0 as infinity for "Best Rate" (ascending) to keep data artifacts at bottom
            deduped.sort(
                key=lambda x: x["price_per_sqft"] if x["price_per_sqft"] > 0 else float("inf")
            )

        return deduped[:limit]
