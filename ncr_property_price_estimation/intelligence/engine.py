"""
NCR Advanced Intelligence Engine (V28).

Calculates Yield, Risk, and Investment Scores using Cross-Model analysis.

Optimizations (V28.1):
- evaluate_property() now accepts typed scalars (not raw dicts), eliminating
  the estimated_total_price / estimated_market_value key mismatch.
- Risk scoring now defaults to geo_median from the feature pipeline when no
  H3 cell data is available (was always '0', which silently disabled all labels).
- ROI calculation accepts is_near_metro as a typed bool, not the full input dict.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


class IntelligenceEngine:
    """
    Advanced Intelligence Layer (V28).
    Calculates Yield, Risk, and Investment Scores using Cross-Model analysis.
    """

    @staticmethod
    def calculate_yield(total_price: float, monthly_rent: float) -> float:
        """
        Calculate Annualized Gross Rental Yield.
        Yield % = (Monthly Rent × 12) / Total Value × 100
        """
        if total_price <= 0:
            return 0.0
        return round((monthly_rent * 12) / total_price * 100, 2)

    @staticmethod
    def calculate_risk_score(
        predicted_price: float,
        reference_median: float,
        geo_confidence: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Detect over/under-pricing vs. the locality reference median.

        Score interpretation:
            0–35   → Value Pick (underpriced vs. micro-market)
            35–65  → Fair Value
            65–85  → Premium Area
            85–100 → High Risk / Overvalued

        Args:
            predicted_price:  Estimated total market value (₹).
            reference_median: Locality geo-median from GeoMedianEncoder (₹/sqft log-scale).
                              Defaults to global training median if sector has low support.
            geo_confidence:   Reserved for H3 cell reliability weight (future use).
        """
        if reference_median <= 0 or np.isnan(reference_median):
            return {"score": 50, "label": "Unknown (Low Data)"}

        # Z-Score relative to micro-market median
        z_score = (predicted_price - reference_median) / (reference_median + 1e-9)

        # Risk score: 50 = fair value baseline ± z-score scaled to 0-100
        base_score = 50 + (z_score * 50)
        final_score = float(np.clip(base_score, 0, 100))

        if final_score < 35:
            label = "Value Pick"
        elif final_score < 65:
            label = "Fair Value"
        elif final_score < 85:
            label = "Premium Area"
        else:
            label = "High Risk / Overvalued"

        return {"score": round(final_score, 1), "label": label}

    @staticmethod
    def calculate_roi_index(
        yield_pct: float,
        is_near_metro: bool,
        risk_score: float,
    ) -> float:
        """
        Composite investment index (0–10).
        Rewards high yield and metro proximity. Penalises high risk.
        """
        # Yield contribution: normalize 2–6% range to 0–5 scale
        yield_score = np.clip((yield_pct - 2) * 1.25, 0, 5)

        # Metro proximity bonus
        metro_bonus = 2.0 if is_near_metro else 0.0

        # Risk penalty: max 3 points deducted at 100% risk score
        risk_penalty = (risk_score / 100) * 3.0

        final_roi = 5.0 + yield_score + metro_bonus - risk_penalty
        return round(float(np.clip(final_roi, 0, 10)), 1)

    def evaluate_property(
        self,
        total_price: float,
        monthly_rent: float,
        is_near_metro: bool,
        geo_median: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Single entry point for comprehensive investment evaluation.

        Args:
            total_price:    Predicted total market value in ₹ (price_per_sqft × area).
            monthly_rent:   Predicted monthly rent in ₹ (rent_per_sqft × area).
            is_near_metro:  Whether property is within 500m of a metro station.
            geo_median:     Locality price reference from GeoMedianEncoder output.
                            Defaults to 0.0 (→ Unknown risk label).
        """
        y_pct = self.calculate_yield(total_price, monthly_rent)
        risk = self.calculate_risk_score(total_price, geo_median)
        roi = self.calculate_roi_index(y_pct, is_near_metro, risk["score"])

        return {
            "rental_yield_pct": y_pct,
            "investment_roi_index": roi,
            "risk_analysis": risk,
            "annual_rent_return": round(monthly_rent * 12, 2),
        }

    @staticmethod
    def recommend_alternatives(
        locality_index: Dict[str, Any],
        current_city: str,
        current_sector: str,
        user_budget_sqft: float,
        current_yield: float
    ) -> list[Dict[str, Any]]:
        """
        Suggest Top 5 alternative localities in the same city based on Value, Yield, and Data Confidence.
        """
        city_data = locality_index.get(current_city, {})
        alternatives = []
        
        # Budget range: ±30%
        min_budget = user_budget_sqft * 0.70
        max_budget = user_budget_sqft * 1.30
        
        for loc, data in city_data.items():
            if loc == current_sector:
                continue
                
            price = data.get("median_price_sqft", 0)
            y = data.get("gross_yield_pct", 0)
            count = data.get("listing_count", 0)
            
            if min_budget <= price <= max_budget:
                # Composite score
                # Yield Score (40%): Higher yield = better (approx max 8%)
                yield_score = min(y / 8.0, 1.0) * 40
                
                # Value Score (30%): Lower price = better
                value_score = (1.0 - (price / max_budget)) * 30
                
                # Data Confidence (30%): More listings = more reliable (approx max 500)
                conf_score = min(count / 500.0, 1.0) * 30
                
                composite_score = yield_score + value_score + conf_score
                
                alternatives.append({
                    "locality": loc,
                    "median_price_sqft": price,
                    "expected_yield_pct": y,
                    "listing_count": count,
                    "top_societies": data.get("top_societies", []),
                    "composite_score": round(composite_score, 2)
                })
                
        # Sort by composite score descending
        alternatives.sort(key=lambda x: x["composite_score"], reverse=True)
        return alternatives[:5]

    @staticmethod
    def find_similar_listings(
        pool_df: pd.DataFrame,
        city: str,
        listing_type: str,
        target_price: float,
        target_area: float,
        target_bhk: int
    ) -> list[Dict[str, Any]]:
        """
        Discover Top 5 real-world historical listings matching the search criteria.
        """
        if pool_df.empty:
            return []
            
        # 1. Broad Filter (City + Listing Type)
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(city, city)
        mask = (pool_df["city"] == db_city) & (pool_df["listing_type"].str.lower() == listing_type.lower())
        df = pool_df[mask].copy()
        
        if df.empty:
            return []
            
        # 2. BHK Matching (Exact if possible, then +/- 1)
        bhk_mask = df["bedrooms"] == target_bhk
        if bhk_mask.sum() < 5:
            # Fallback to +/- 1 BHK if too few exact matches
            bhk_mask = (df["bedrooms"] >= target_bhk - 1) & (df["bedrooms"] <= target_bhk + 1)
        
        df = df[bhk_mask].copy()
        
        # 3. Price & Area Range (±30% for discovery)
        p_min, p_max = target_price * 0.7, target_price * 1.3
        a_min, a_max = target_area * 0.7, target_area * 1.3
        
        range_mask = (df["total_price"].between(p_min, p_max)) & (df["area"].between(a_min, a_max))
        matches = df[range_mask].copy()
        
        if matches.empty:
            # If nothing in range, just take closest BHK ones
            matches = df.head(50).copy()
            
        # 4. Scoring Proximity
        # Lower absolute distance = better
        price_dist = (matches["total_price"] - target_price).abs() / target_price
        area_dist = (matches["area"] - target_area).abs() / target_area
        
        matches["similarity_score"] = 1.0 - (price_dist * 0.5 + area_dist * 0.5)
        
        # 5. Format & Return
        top_matches = matches.sort_values("similarity_score", ascending=False).head(5)
        
        results = []
        for _, row in top_matches.iterrows():
            results.append({
                "society": str(row["society_name"]),
                "locality": str(row["sector"]),
                "price": round(float(row["total_price"]), 0),
                "area": round(float(row["area"]), 0),
                "bhk": int(row["bedrooms"]) if pd.notna(row["bedrooms"]) else 0,
                "price_sqft": round(float(row["price_per_sqft"]), 0),
                "latitude": float(row["latitude"]) if pd.notna(row.get("latitude")) else None,
                "longitude": float(row["longitude"]) if pd.notna(row.get("longitude")) else None,
                "h3_median_price": float(row.get("h3_median_price", 0)),
                "value_score": round((row.get("h3_median_price", 0) - row["price_per_sqft"]) / row["h3_median_price"], 3) if row.get("h3_median_price", 0) > 0 else 0
            })
            
        return results

    def discover_properties(
        self,
        pool_df: pd.DataFrame,
        locality_index: Dict[str, Any],
        city: str,
        listing_type: str,
        bhk_list: list[int],
        budget_min: float,
        budget_max: float,
        area_min: float | None = None,
        area_max: float | None = None,
        sort_by: str = "yield",
        limit: int = 20
    ) -> list[Dict[str, Any]]:
        """
        Discover Enriched Properties for Recommender UI.
        """
        if pool_df.empty:
            return []

        # 1. Broad Filter (City + Listing Type)
        db_city = {"Gurugram": "Gurgaon", "Greater Noida": "Greater_Noida"}.get(city, city)
        mask = (pool_df["city"] == db_city) & (pool_df["listing_type"].str.lower() == listing_type.lower())
        
        # 2. BHK Matching
        if bhk_list:
            mask = mask & (pool_df["bedrooms"].isin(bhk_list))
            
        # 3. Budget Range
        mask = mask & (pool_df["total_price"].between(budget_min, budget_max))
        
        # 4. Area Range
        if area_min is not None:
            mask = mask & (pool_df["area"] >= area_min)
        if area_max is not None:
            mask = mask & (pool_df["area"] <= area_max)
            
        df = pool_df[mask].copy()
        
        if df.empty:
            return []
            
        # Enrich with Intelligence Metrics
        results = []
        for _, row in df.iterrows():
            loc = str(row["sector"])
            area = float(row["area"])
            price = float(row["total_price"])
            price_sqft = float(row["price_per_sqft"])
            
            loc_data = locality_index.get(city, {}).get(loc, {})
            geo_median_price_sqft = loc_data.get("median_price_sqft", 0)
            geo_median_rent_sqft = loc_data.get("median_rent_sqft", 0)
            
            monthly_rent = 0.0
            total_price = 0.0
            
            if listing_type.lower() == "buy":
                total_price = price
                # approximate rent from locality index
                monthly_rent = (geo_median_rent_sqft * area) if geo_median_rent_sqft > 0 else (price * 0.03 / 12)
            else:
                monthly_rent = price
                # approximate total price from locality index
                total_price = (geo_median_price_sqft * area) if geo_median_price_sqft > 0 else (monthly_rent * 12 / 0.03)

            y_pct = self.calculate_yield(total_price, monthly_rent)
            risk = self.calculate_risk_score(total_price, geo_median_price_sqft * area if geo_median_price_sqft else 0)
            roi_index = self.calculate_roi_index(y_pct, False, risk["score"]) 

            # Value Analysis
            h3_median = float(row.get("h3_median_price", 0))
            benchmark = h3_median if h3_median > 0 else geo_median_price_sqft
            value_score = (benchmark - price_sqft) / benchmark if benchmark > 0 else 0
            
            results.append({
                "society": str(row["society_name"]),
                "locality": loc,
                "city": city,
                "price": price,
                "area": area,
                "bhk": int(row["bedrooms"]) if pd.notna(row["bedrooms"]) else 0,
                "price_sqft": price_sqft,
                "rental_yield_pct": y_pct,
                "roi_index": roi_index,
                "listing_type": listing_type.lower(),
                "latitude": float(row["latitude"]) if pd.notna(row.get("latitude")) else None,
                "longitude": float(row["longitude"]) if pd.notna(row.get("longitude")) else None,
                "h3_median_price": h3_median,
                "value_score": round(value_score, 3)
            })
            
        # Sort
        if sort_by == "yield":
            results.sort(key=lambda x: x["rental_yield_pct"], reverse=True)
        elif sort_by == "roi":
            results.sort(key=lambda x: x["roi_index"], reverse=True)
        elif sort_by == "price_low":
            results.sort(key=lambda x: x["price"], reverse=False)
        elif sort_by == "price_high":
            results.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "area":
            results.sort(key=lambda x: x["area"], reverse=True)

        return results[:limit]
