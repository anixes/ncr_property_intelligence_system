"""
Feature pipeline unit tests.

Tests run on small synthetic data (from conftest fixtures).
No trained models or real data files required.
"""

import numpy as np
import pandas as pd
import pytest

from ncr_property_price_estimation.features import (
    FeatureCreator,
    GeoMedianEncoder,
    Winsorizer,
    build_feature_pipeline,
)

# ---------------------------------------------------------------------------
# FeatureCreator
# ---------------------------------------------------------------------------


class TestFeatureCreator:
    def test_adds_expected_columns(self, sample_df):
        creator = FeatureCreator()
        result = creator.fit_transform(sample_df)

        for col in ["log_area", "area_per_bedroom", "bathrooms_missing", "floor_missing"]:
            assert col in result.columns, f"Missing column: {col}"

    def test_log_area_values(self, sample_df):
        result = FeatureCreator().fit_transform(sample_df)
        expected = np.log1p(sample_df["area"])
        np.testing.assert_array_almost_equal(result["log_area"], expected)

    def test_area_per_bedroom(self, sample_df):
        result = FeatureCreator().fit_transform(sample_df)
        # bedrooms > 0 → area / bedrooms
        mask = sample_df["bedrooms"] > 0
        expected = sample_df.loc[mask, "area"] / sample_df.loc[mask, "bedrooms"]
        np.testing.assert_array_almost_equal(result.loc[mask, "area_per_bedroom"], expected)

    def test_missing_indicators(self, sample_df):
        result = FeatureCreator().fit_transform(sample_df)
        # Row index 2 has NaN bathrooms
        assert result.loc[2, "bathrooms_missing"] == 1
        # Row index 1 has NaN floor
        assert result.loc[1, "floor_missing"] == 1
        # Row index 0 has both present
        assert result.loc[0, "bathrooms_missing"] == 0
        assert result.loc[0, "floor_missing"] == 0

    def test_does_not_mutate_input(self, sample_df):
        original_cols = list(sample_df.columns)
        FeatureCreator().fit_transform(sample_df)
        assert list(sample_df.columns) == original_cols


# ---------------------------------------------------------------------------
# Winsorizer
# ---------------------------------------------------------------------------


class TestWinsorizer:
    def test_clips_extremes(self):
        X = np.array([[1], [2], [3], [4], [100]])
        w = Winsorizer(lower_q=0.0, upper_q=0.8)
        result = w.fit_transform(X)
        upper_bound = np.quantile(X, 0.8, axis=0)
        assert result.max() <= upper_bound

    def test_identity_within_bounds(self):
        X = np.array([[5], [6], [7], [8], [9]])
        w = Winsorizer(lower_q=0.0, upper_q=1.0)
        result = w.fit_transform(X)
        np.testing.assert_array_equal(X, result)


# ---------------------------------------------------------------------------
# GeoMedianEncoder
# ---------------------------------------------------------------------------


class TestGeoMedianEncoder:
    def test_fit_transform_produces_geo_median(self, sample_df, sample_target):
        enc = GeoMedianEncoder(min_support=1)
        result = enc.fit_transform(sample_df, sample_target)

        assert "geo_median" in result.columns
        assert "city" not in result.columns, "city column should be dropped"
        assert "sector" not in result.columns, "sector column should be dropped"

    def test_geo_median_not_null(self, sample_df, sample_target):
        enc = GeoMedianEncoder(min_support=1)
        result = enc.fit_transform(sample_df, sample_target)
        assert result["geo_median"].notna().all()

    def test_unseen_city_falls_back_to_global(self, sample_df, sample_target):
        """Unseen city at inference time → should get global median, not crash."""
        enc = GeoMedianEncoder(min_support=1)
        enc.fit(sample_df, sample_target)

        unseen = pd.DataFrame(
            {
                "area": [1000.0],
                "bedrooms": [2],
                "bathrooms": [1.0],
                "balcony": [1],
                "floor": [3.0],
                "prop_type": ["Apartment"],
                "furnished": ["Unfurnished"],
                "facing": ["North"],
                "city": ["Lucknow"],  # never seen during fit
                "sector": ["Gomti Nagar"],  # never seen during fit
                "pooja_room": [0],
                "servant_room": [0],
                "store_room": [0],
                "pool": [0],
                "gym": [0],
                "lift": [1],
                "parking": [1],
                "vastu_compliant": [0],
            }
        )

        result = enc.transform(unseen)

        assert "geo_median" in result.columns
        assert result["geo_median"].notna().all(), "Unseen city should fallback, not NaN"
        assert result["geo_median"].iloc[0] == pytest.approx(enc.global_median_)

    def test_unseen_sector_falls_back_to_city(self, sample_df, sample_target):
        """Known city, unknown sector → should get city median."""
        enc = GeoMedianEncoder(min_support=1)
        enc.fit(sample_df, sample_target)

        unseen_sector = pd.DataFrame(
            {
                "area": [1000.0],
                "bedrooms": [2],
                "bathrooms": [1.0],
                "balcony": [1],
                "floor": [3.0],
                "prop_type": ["Apartment"],
                "furnished": ["Unfurnished"],
                "facing": ["North"],
                "city": ["Gurugram"],  # known city
                "sector": ["Sector 999"],  # unknown sector
                "pooja_room": [0],
                "servant_room": [0],
                "store_room": [0],
                "pool": [0],
                "gym": [0],
                "lift": [1],
                "parking": [1],
                "vastu_compliant": [0],
            }
        )

        result = enc.transform(unseen_sector)
        expected_city_median = enc.city_median_["Gurugram"]
        assert result["geo_median"].iloc[0] == pytest.approx(expected_city_median)


# ---------------------------------------------------------------------------
# build_feature_pipeline structure
# ---------------------------------------------------------------------------


class TestPipelineStructure:
    def test_has_expected_step_names(self):
        """Assert step names exist — not rigid class assertions."""
        from sklearn.linear_model import Ridge

        pipe = build_feature_pipeline(Ridge())
        step_names = [name for name, _ in pipe.steps]

        assert "feature_creator" in step_names
        assert "geo_encoder" in step_names
        assert "preprocessor" in step_names
        assert "model" in step_names

    def test_model_step_is_last(self):
        from sklearn.linear_model import Ridge

        pipe = build_feature_pipeline(Ridge())
        last_name, _ = pipe.steps[-1]
        assert last_name == "model"

    def test_preprocessor_has_num_and_cat(self):
        from sklearn.linear_model import Ridge

        pipe = build_feature_pipeline(Ridge())
        preprocessor = pipe.named_steps["preprocessor"]
        transformer_names = [name for name, _, _ in preprocessor.transformers]

        assert "num" in transformer_names
        assert "cat" in transformer_names
