"""
Unit tests for the Discovery Engine — deduplication and sorting.
"""

import pandas as pd

from ncr_property_price_estimation.discovery.discover_engine import DiscoverEngine
from ncr_property_price_estimation.schemas import DiscoverRequest


class TestDiscoveryDeduplication:
    """Verify Alpha-Normalized deduplication works correctly."""

    @staticmethod
    def _make_pool(rows: list[dict]) -> pd.DataFrame:
        """Create a minimal discovery pool DataFrame."""
        defaults = {
            "city": "Gurgaon",
            "sector": "Sector 50",
            "society": "Test Society",
            "listing_type": "buy",
            "bedrooms": 3,
            "bathrooms": 2,
            "area": 1500.0,
            "price_per_sqft": 10000.0,
            "h3_res8": "882a100d2dfffff",
            "h3_median_price": 15000000.0,
            "h3_listings_count": 10,
            "total_price": 15000000.0,
            "latitude": 28.46,
            "longitude": 77.03,
        }
        full_rows = []
        for row in rows:
            full_row = {**defaults, **row}
            full_rows.append(full_row)
        return pd.DataFrame(full_rows)

    def test_duplicate_society_keeps_lowest_price(self):
        """Same society + area + bhk should only keep the cheapest listing."""
        pool = self._make_pool(
            [
                {"society": "Palm Heights", "total_price": 15000000, "price_per_sqft": 10000},
                {"society": "Palm Heights", "total_price": 12000000, "price_per_sqft": 8000},
                {"society": "Palm Heights", "total_price": 18000000, "price_per_sqft": 12000},
            ]
        )

        req = DiscoverRequest(
            city="Gurgaon",
            listing_type="buy",
            bhk=[3],
            budget_min=10000000,
            budget_max=20000000
        )

        results = DiscoverEngine.discover_properties(
            pool_df=pool,
            locality_index={},
            req=req
        )

        assert len(results) == 1
        assert results[0]["price"] == 12000000

    def test_alpha_normalization_ignores_spaces(self):
        """'Palm Heights' and 'Palm  Heights' should be treated as duplicates."""
        pool = self._make_pool(
            [
                {"society": "Palm Heights", "total_price": 15000000, "price_per_sqft": 10000},
                {"society": "Palm  Heights", "total_price": 12000000, "price_per_sqft": 8000},
            ]
        )

        req = DiscoverRequest(
            city="Gurgaon",
            listing_type="buy",
            bhk=[3],
            budget_min=10000000,
            budget_max=20000000
        )

        results = DiscoverEngine.discover_properties(
            pool_df=pool,
            locality_index={},
            req=req
        )

        assert len(results) == 1

    def test_different_societies_not_deduped(self):
        """Different societies should NOT be deduped."""
        pool = self._make_pool(
            [
                {"society": "Palm Heights", "total_price": 15000000, "price_per_sqft": 10000},
                {"society": "Maple Tower", "total_price": 14000000, "price_per_sqft": 9333},
            ]
        )

        req = DiscoverRequest(
            city="Gurgaon",
            listing_type="buy",
            bhk=[3],
            budget_min=10000000,
            budget_max=20000000
        )

        results = DiscoverEngine.discover_properties(
            pool_df=pool,
            locality_index={},
            req=req
        )

        assert len(results) == 2

    def test_sort_by_score(self):
        """Sort by 'score' should order by unified_score descending."""
        pool = self._make_pool(
            [
                {"society": "Cheap Place", "total_price": 11000000, "price_per_sqft": 7333},
                {"society": "Mid Place", "total_price": 14000000, "price_per_sqft": 9333},
                {"society": "Expensive Place", "total_price": 19000000, "price_per_sqft": 12666},
            ]
        )

        req = DiscoverRequest(
            city="Gurgaon",
            listing_type="buy",
            bhk=[3],
            budget_min=10000000,
            budget_max=20000000,
            sort_by="score"
        )

        results = DiscoverEngine.discover_properties(
            pool_df=pool,
            locality_index={},
            req=req
        )

        if len(results) >= 2:
            scores = [r["unified_score"] for r in results]
            assert scores == sorted(scores, reverse=True)

    def test_sort_by_price_low(self):
        """Sort by 'price_low' should order by price ascending."""
        pool = self._make_pool(
            [
                {"society": "B Place", "total_price": 18000000, "price_per_sqft": 12000},
                {"society": "A Place", "total_price": 11000000, "price_per_sqft": 7333},
            ]
        )

        req = DiscoverRequest(
            city="Gurgaon",
            listing_type="buy",
            bhk=[3],
            budget_min=10000000,
            budget_max=20000000,
            sort_by="price_low"
        )

        results = DiscoverEngine.discover_properties(
            pool_df=pool,
            locality_index={},
            req=req
        )

        if len(results) >= 2:
            prices = [r["price"] for r in results]
            assert prices == sorted(prices)
