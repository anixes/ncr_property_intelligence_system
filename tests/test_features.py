"""
Feature engineering pipeline unit tests.

Tests run on small synthetic data (from conftest fixtures).
No trained models or real data files required.
"""

import numpy as np
import pandas as pd
import pytest

from ncr_property_price_estimation.features import (
    FeatureCreator,
    Winsorizer,
    MicroMarketEncoder,
    build_catboost_pipeline,
)

# ---------------------------------------------------------------------------
# FeatureCreator
# ---------------------------------------------------------------------------


class TestFeatureCreator:
    def test_adds_expected_columns(self, sample_df):
        creator = FeatureCreator()
        result = creator.fit_transform(sample_df)

        for col in ["log_area", "area_per_bedroom", "bathrooms_missing"]:
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
        # We manually set one bathroom to NaN for test
        df = sample_df.copy()
        df.loc[0, "bathrooms"] = np.nan
        result = FeatureCreator().fit_transform(df)
        
        assert result.loc[0, "bathrooms_missing"] == 1
        assert result.loc[1, "bathrooms_missing"] == 0

    def test_does_not_mutate_input(self, sample_df):
        original_cols = list(sample_df.columns)
        FeatureCreator().fit_transform(sample_df)
        assert list(sample_df.columns) == original_cols


# ---------------------------------------------------------------------------
# Winsorizer
# ---------------------------------------------------------------------------


class TestWinsorizer:
    def test_clips_extremes(self, sample_df):
        # High area outlier
        df = sample_df.copy()
        df.loc[0, "area"] = 100000 
        
        w = Winsorizer(lower_q=0.0, upper_q=0.8, bypass_luxury=False)
        w.fit(df[["area", "is_luxury"]])
        result = w.transform(df[["area", "is_luxury"]])
        
        upper_bound = np.quantile(df["area"], 0.8)
        assert result["area"].max() <= upper_bound

    def test_luxury_bypass(self, sample_df):
        """Ultra-luxury areas (is_luxury=1) should not be clipped."""
        df = sample_df.copy()
        # Row 2 is luxury (is_luxury=1) in our conftest sample_df
        df.loc[2, "area"] = 50000 
        
        w = Winsorizer(lower_q=0.0, upper_q=0.5, bypass_luxury=True)
        w.fit(df[["area", "is_luxury"]])
        result = w.transform(df[["area", "is_luxury"]])
        
        # Row 2 should remain 50000, others clipped to median
        assert result.loc[2, "area"] == 50000
        assert result.loc[0, "area"] < 50000


# ---------------------------------------------------------------------------
# MicroMarketEncoder
# ---------------------------------------------------------------------------


class TestMicroMarketEncoder:
    def test_adds_geo_median(self, sample_df, sample_target):
        enc = MicroMarketEncoder(min_support_soc=1, min_support_sec=1)
        result = enc.fit_transform(sample_df, sample_target)
        assert "geo_median" in result.columns

    def test_fallback_logic(self, sample_df, sample_target):
        enc = MicroMarketEncoder(min_support_soc=10, min_support_sec=10)
        enc.fit(sample_df, sample_target)
        
        unseen = pd.DataFrame({
            "city": ["Mars"],
            "sector": ["Sector 1"],
            "society": ["Unknown"]
        })
        
        result = enc.transform(unseen)
        assert result["geo_median"].iloc[0] == pytest.approx(enc.global_median_)

    def test_bypass_drop(self, sample_df, sample_target):
        enc = MicroMarketEncoder(bypass_drop=True)
        result = enc.fit_transform(sample_df, sample_target)
        assert "city" in result.columns
        assert "society" in result.columns


# ---------------------------------------------------------------------------
# build_catboost_pipeline structure
# ---------------------------------------------------------------------------


class TestPipelineStructure:
    def test_has_expected_step_names(self):
        from catboost import CatBoostRegressor
        pipe = build_catboost_pipeline(CatBoostRegressor(iterations=1))
        step_names = [name for name, _ in pipe.steps]

        assert "city_normalizer" in step_names
        assert "feature_creator" in step_names
        assert "geo_encoder" in step_names
        assert "preprocessor" in step_names
        assert "model" in step_names

    def test_preprocessor_has_num_and_cat(self):
        from catboost import CatBoostRegressor
        pipe = build_catboost_pipeline(CatBoostRegressor(iterations=1))
        preprocessor = pipe.named_steps["preprocessor"]
        transformer_names = [name for name, _, _ in preprocessor.transformers]

        assert "num" in transformer_names
        assert "cat" in transformer_names
