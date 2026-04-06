from typing import Any

from ncr_property_price_estimation.discovery.comparables import ComparablesEngine
from ncr_property_price_estimation.discovery.discover_engine import DiscoverEngine
from ncr_property_price_estimation.intelligence.recommendations import RecommendationEngine
from ncr_property_price_estimation.intelligence.risk_engine import RiskEngine
from ncr_property_price_estimation.intelligence.roi_engine import ROIEngine
from ncr_property_price_estimation.intelligence.scoring_engine import ScoringEngine


class IntelligenceEngine:
    """
    Facade for the NCR Intelligence Suite.
    Delegates to modular specialized engines.
    """

    def __init__(self):
        self.scoring = ScoringEngine()
        self.roi = ROIEngine()
        self.risk = RiskEngine()
        self.recommendations = RecommendationEngine()
        self.comparables = ComparablesEngine()
        self.discovery = DiscoverEngine()

    def evaluate_property(
        self,
        total_price: float,
        monthly_rent: float,
        is_near_metro: bool,
        geo_median: float = 0.0,
        demand_index: float = 5.0,
        intent: str = "buy",
    ) -> dict[str, Any]:
        """
        Comprehensive investment evaluation via sub-engines.
        Pivots logic based on 'buy' (ROI focus) or 'rent' (Utility focus).
        """
        y_pct = self.roi.calculate_yield(total_price, monthly_rent)

        # Risk target depends on intent
        risk_target = total_price if intent == "buy" else monthly_rent
        risk_info = self.risk.calculate_risk_score(risk_target, geo_median, intent=intent)

        overval_pct = 0.0
        if geo_median > 0:
            overval_pct = (risk_target - geo_median) / geo_median * 100

        # Normalize risk from 0–100 scale to 0–10 for scoring engine
        normalized_risk = risk_info["score"] / 10.0

        unified_score = self.scoring.calculate_unified_score(
            yield_pct=y_pct,
            overvaluation_pct=overval_pct,
            is_near_metro=is_near_metro,
            risk_index=normalized_risk,
            demand_index=demand_index,
            intent=intent,
        )

        return {
            "yield_pct": y_pct,
            "unified_score": unified_score,
            "risk_analysis": risk_info,
            "overvaluation_pct": round(overval_pct, 2),
            "annual_rent_return": self.roi.calculate_annual_rent(monthly_rent),
        }

    def recommend_alternatives(self, *args, **kwargs):
        return self.recommendations.recommend_alternatives(*args, **kwargs)

    def find_similar_listings(self, *args, **kwargs):
        return self.comparables.find_similar_listings(*args, **kwargs)

    def discover_properties(self, *args, **kwargs):
        return self.discovery.discover_properties(*args, **kwargs)
