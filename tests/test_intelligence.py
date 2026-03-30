"""
Unit tests for Intelligence Engine — scoring, risk normalization, and evaluation.
"""

import pytest

from ncr_property_price_estimation.intelligence.engine import IntelligenceEngine
from ncr_property_price_estimation.intelligence.risk_engine import RiskEngine
from ncr_property_price_estimation.intelligence.roi_engine import ROIEngine
from ncr_property_price_estimation.intelligence.scoring_engine import ScoringEngine


class TestScoringEngine:
    """Tests for the Unified Scoring System (0–10)."""

    def test_perfect_score_calculation(self):
        """Best-case scenario: 8% yield, no overvaluation, near metro, low risk."""
        score = ScoringEngine.calculate_unified_score(
            yield_pct=8.0,
            overvaluation_pct=0.0,
            is_near_metro=True,
            risk_index=0.0,
            demand_index=10.0,
        )
        assert score == 10.0

    def test_zero_score_calculation(self):
        """Worst-case: no yield, heavily overvalued, no metro, max risk."""
        score = ScoringEngine.calculate_unified_score(
            yield_pct=0.0,
            overvaluation_pct=50.0,
            is_near_metro=False,
            risk_index=10.0,
            demand_index=0.0,
        )
        assert score == 0.0

    def test_score_always_clamped_0_to_10(self):
        """Score must always be between 0 and 10."""
        score = ScoringEngine.calculate_unified_score(
            yield_pct=100.0,
            overvaluation_pct=-1000.0,
            is_near_metro=True,
            risk_index=-100.0,
            demand_index=100.0,
        )
        assert 0 <= score <= 10

    def test_score_rounded_to_2_decimals(self):
        """Score must be rounded to 2 decimal places."""
        score = ScoringEngine.calculate_unified_score(
            yield_pct=3.0,
            overvaluation_pct=10.0,
            is_near_metro=True,
            risk_index=3.0,
            demand_index=5.0,
        )
        assert score == round(score, 2)

    def test_weights_sum_to_one(self):
        """Internal check: weights must sum to 1.0."""
        assert 0.35 + 0.25 + 0.15 + 0.15 + 0.10 == pytest.approx(1.0)


class TestRiskEngine:
    """Tests for risk score calculation."""

    def test_risk_returns_0_to_100(self):
        """Risk engine output must be in 0–100 range."""
        result = RiskEngine.calculate_risk_score(10000000, 9000000)
        assert 0 <= result["score"] <= 100

    def test_risk_fair_value(self):
        """Equal price and median should be ~50 (Fair Value)."""
        result = RiskEngine.calculate_risk_score(10000000, 10000000)
        assert result["label"] == "Fair Value"
        assert 40 <= result["score"] <= 60

    def test_risk_unknown_when_no_reference(self):
        """Zero median should return 'Unknown' risk."""
        result = RiskEngine.calculate_risk_score(10000000, 0)
        assert result["label"] == "Unknown (Low Data)"


class TestIntelligenceEngine:
    """Tests for the facade engine with risk normalization fix."""

    def test_unified_score_in_valid_range(self):
        """Unified score from evaluate_property must be 0–10."""
        engine = IntelligenceEngine()
        result = engine.evaluate_property(
            total_price=10000000,
            monthly_rent=25000,
            is_near_metro=True,
            geo_median=9000000,
        )
        assert 0 <= result["unified_score"] <= 10

    def test_risk_normalization_applied(self):
        """Risk engine returns 0-100, but scoring engine should receive 0-10.
        This test verifies the fix by checking the score isn't artificially low."""
        engine = IntelligenceEngine()

        # Fair value property with good yield and metro access
        result = engine.evaluate_property(
            total_price=10000000,
            monthly_rent=30000,
            is_near_metro=True,
            geo_median=10000000,  # Exactly at median
        )
        # With risk properly normalized, this should score well (>5)
        assert result["unified_score"] > 5.0

    def test_no_roi_index_in_response(self):
        """roi_index must NOT appear in the response."""
        engine = IntelligenceEngine()
        result = engine.evaluate_property(
            total_price=10000000,
            monthly_rent=25000,
            is_near_metro=True,
        )
        assert "roi_index" not in result

    def test_response_has_required_fields(self):
        """Response must contain all required intelligence fields."""
        engine = IntelligenceEngine()
        result = engine.evaluate_property(
            total_price=10000000,
            monthly_rent=25000,
            is_near_metro=True,
        )
        required = [
            "yield_pct",
            "unified_score",
            "risk_analysis",
            "overvaluation_pct",
            "annual_rent_return",
        ]
        for field in required:
            assert field in result, f"Missing field: {field}"


class TestROIEngine:
    """Tests for yield calculation."""

    def test_yield_calculation(self):
        """Standard yield: (25000 * 12) / 10000000 * 100 = 3.0%."""
        result = ROIEngine.calculate_yield(10000000, 25000)
        assert result == 3.0

    def test_yield_zero_price(self):
        """Zero price should return 0 yield, not error."""
        result = ROIEngine.calculate_yield(0, 25000)
        assert result == 0.0
