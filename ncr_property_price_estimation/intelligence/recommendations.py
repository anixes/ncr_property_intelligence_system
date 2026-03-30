import math
from typing import Any


class RecommendationEngine:
    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points in km."""
        if None in [lat1, lon1, lat2, lon2]:
            return 999.0
        R = 6371.0  # Radius of earth in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def recommend_alternatives(
        locality_index: dict[str, Any],
        current_city: str,
        current_sector: str,
        user_budget_sqft: float,
        current_yield: float,
        current_lat: float = None,
        current_lon: float = None,
    ) -> list[dict[str, Any]]:
        """
        Suggest Top 5 alternative localities in the same city based on Value, Yield, and Data Confidence.
        Includes strict filtering for Unknowns and Outliers.
        """
        city_data = locality_index.get(current_city, {})
        alternatives = []

        # Budget range: ±30%
        min_budget = user_budget_sqft * 0.70
        max_budget = user_budget_sqft * 1.30

        for loc, data in city_data.items():
            # 1. Strict Filtering: No Unknowns, No current sector, No zero values
            if loc == current_sector or loc == "Unknown":
                continue

            price = data.get("median_price_sqft", 0)
            y = data.get("gross_yield_pct", 0)
            count = data.get("listing_count", 0)
            rec_lat = data.get("lat")
            rec_lon = data.get("lon")

            if price <= 0 or y <= 0:
                continue

            # 2. Distance Filter (V2 Strict: < 8km)
            if current_lat and current_lon and rec_lat and rec_lon:
                distance = RecommendationEngine.haversine(
                    current_lat, current_lon, rec_lat, rec_lon
                )
                if distance > 8.0:
                    continue
            elif current_lat:
                # If we have target coordinates but candidate doesn't, we skip for safety in V2
                continue

            # 3. Outlier Filters
            if price < 2000 or price > 100000:
                continue

            if min_budget <= price <= max_budget:
                # Compute distance for response
                distance_km = 0.0
                if current_lat and current_lon and rec_lat and rec_lon:
                    distance_km = RecommendationEngine.haversine(
                        current_lat, current_lon, rec_lat, rec_lon
                    )

                # Composite score (weighted normalization)
                # Yield Score (50%), Value Score (30%), confidence (20%)
                yield_score = min(y / 8 * 10, 10)
                # For alternatives, price score is relative to target
                value_score = max(0, 10 - (price / min_budget) * 2)
                conf_score = min(count / 500.0, 1.0) * 10

                composite_score = (yield_score * 0.5) + (value_score * 0.3) + (conf_score * 0.2)

                alternatives.append(
                    {
                        "locality": loc,
                        "city": current_city,
                        "median_price_sqft": round(price, 0),
                        "expected_yield_pct": round(y, 2),
                        "distance_km": round(distance_km, 1),
                        "listing_count": count,
                        "top_societies": data.get("top_societies", []),
                        "composite_score": round(composite_score, 2),
                    }
                )

        # Sort by composite score descending
        alternatives.sort(key=lambda x: x["composite_score"], reverse=True)
        return alternatives[:5]
