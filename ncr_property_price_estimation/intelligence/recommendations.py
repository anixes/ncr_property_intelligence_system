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
        Resilient filtering: falls back to wider bands if few results are found.
        """
        city_data = locality_index.get(current_city, {})

        # 1. First Pass: Strict (±30% budget, < 10km distance)
        candidates = RecommendationEngine._find_candidates(
            city_data, current_sector, user_budget_sqft, 0.30, 10.0, current_lat, current_lon
        )

        # 2. Second Pass: If sparse, loosen budget to ±50% and distance to 20km
        if len(candidates) < 3:
            candidates = RecommendationEngine._find_candidates(
                city_data, current_sector, user_budget_sqft, 0.50, 20.0, current_lat, current_lon
            )

        # 3. Third Pass: Final desperation (Same city, any budget within reason, ignore distance)
        if len(candidates) < 1:
            candidates = RecommendationEngine._find_candidates(
                city_data, current_sector, user_budget_sqft, 0.80, 999.0, current_lat, current_lon
            )

        # Sort by composite score and return Top 5
        candidates.sort(key=lambda x: x["composite_score"], reverse=True)
        return candidates[:5]

    @staticmethod
    def _find_candidates(
        city_data: dict[str, Any],
        current_sector: str,
        user_budget_sqft: float,
        budget_band: float,
        max_dist_km: float,
        current_lat: float,
        current_lon: float,
    ) -> list[dict[str, Any]]:
        results = []
        min_b = user_budget_sqft * (1 - budget_band)
        max_b = user_budget_sqft * (1 + budget_band)

        for loc, data in city_data.items():
            if loc == current_sector or loc == "Unknown":
                continue

            price = data.get("median_price_sqft", 0)
            y = data.get("gross_yield_pct", 0)
            count = data.get("listing_count", 0)
            rec_lat = data.get("lat")
            rec_lon = data.get("lon")

            # Data Quality: must have a price
            if price <= 0 or price < 1000 or price > 150000:
                continue

            # Fallback yield (City average if missing)
            if y <= 0:
                y = 2.8

            # Distance check
            dist_km = 999.0
            if current_lat and current_lon and rec_lat and rec_lon:
                dist_km = RecommendationEngine.haversine(current_lat, current_lon, rec_lat, rec_lon)
                if dist_km > max_dist_km:
                    continue
            elif current_lat and max_dist_km < 100:
                # Only skip if we explicitly wanted a close distance and have coordinates
                continue

            # Budget check
            if not (min_b <= price <= max_b):
                continue

            # Composite score calculation
            yield_score = min(y / 8 * 10, 10)
            value_score = max(0, 10 - (abs(price - user_budget_sqft) / (user_budget_sqft + 1)) * 10)
            conf_score = min(count / 300.0, 1.0) * 10

            # Penalize distance slightly in score
            dist_penalty = max(0, (dist_km / 10.0)) if dist_km < 500 else 0

            composite_score = (
                (yield_score * 0.4) + (value_score * 0.4) + (conf_score * 0.2) - dist_penalty
            )

            results.append(
                {
                    "locality": loc,
                    "median_price_sqft": round(price, 0),
                    "expected_yield_pct": round(y, 2),
                    "distance_km": round(dist_km, 1) if dist_km < 900 else None,
                    "listing_count": count,
                    "composite_score": round(composite_score, 2),
                    "latitude": rec_lat,
                    "longitude": rec_lon,
                    "h3_index": data.get("h3"),
                }
            )

        return results
