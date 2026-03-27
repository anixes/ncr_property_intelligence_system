"""
Feature engineering pipeline for NCR property price estimation.

All transformations are encapsulated in sklearn-compatible transformers
so that the fitted pipeline is the single deployable artifact.

Pipeline order:
    FeatureCreator → GeoMedianEncoder → ColumnTransformer(num + cat) → Model
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# ---------------------------------------------------------------------------
# Explicit feature lists — no auto-detection
# ---------------------------------------------------------------------------

NUMERIC_FEATURES = [
    "area",
    "bedrooms",
    "bathrooms",
    "log_area",
    "area_per_bedroom",
    "bathrooms_missing",
    "geo_median",
]

CATEGORICAL_FEATURES = [
    "prop_type",
    "furnishing_status",
    "legal_status",
]

# Binary amenity columns (treated as numeric passthrough)
AMENITY_FEATURES = [
    "is_rera_registered",
    "is_luxury",
    "is_gated_community",
    "is_vastu_compliant",
    "is_servant_room",
    "is_study_room",
    "is_store_room",
    "is_pooja_room",
    "has_pool",
    "has_gym",
    "has_lift",
    "is_near_metro",
    "has_power_backup",
    "is_corner_property",
    "is_park_facing",
    "no_brokerage",
    "bachelors_allowed",
    "is_standalone",
    "is_owner_listing",
]


# ---------------------------------------------------------------------------
# 1. Winsorizer
# ---------------------------------------------------------------------------


class Winsorizer(BaseEstimator, TransformerMixin):
    """Clip numeric features at fitted quantile bounds."""

    def __init__(self, lower_q=0.01, upper_q=0.99):
        self.lower_q = lower_q
        self.upper_q = upper_q

    def fit(self, X, y=None):
        self.lower_ = np.nanquantile(X, self.lower_q, axis=0)
        self.upper_ = np.nanquantile(X, self.upper_q, axis=0)
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        return np.clip(X, self.lower_, self.upper_)

    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            return np.asarray(input_features)
        return np.arange(self.n_features_in_).astype(str)


# ---------------------------------------------------------------------------
# 2. FeatureCreator
# ---------------------------------------------------------------------------


class FeatureCreator(BaseEstimator, TransformerMixin):
    """
    Create engineered features from raw model columns.

    New columns:
        log_area          — log1p(area), reduces right skew
        area_per_bedroom  — area / bedrooms, safe division
        bathrooms_missing — binary indicator
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        # Log area
        X["log_area"] = np.log1p(X["area"])

        # Area per bedroom (safe: bedrooms <= 0 or NaN → NaN)
        X["area_per_bedroom"] = np.where(
            X["bedrooms"] > 0,
            X["area"] / X["bedrooms"],
            np.nan,
        )

        # Missing indicators (before imputation fills them)
        X["bathrooms_missing"] = X["bathrooms"].isna().astype(int)

        return X


# ---------------------------------------------------------------------------
# 3. GeoMedianEncoder (Hierarchical Target Encoding)
# ---------------------------------------------------------------------------


class GeoMedianEncoder(BaseEstimator, TransformerMixin):
    """
    Encode geographic location as a single hierarchical median feature.

    Hierarchy:
        1. Sector-level median (if count >= min_support)
        2. City-level median (fallback)
        3. Global median (last resort)

    After encoding, city and sector columns are dropped — their signal
    is captured entirely in the output geo_median column.
    """

    def __init__(self, city_col="city", sector_col="sector", min_support=20):
        self.city_col = city_col
        self.sector_col = sector_col
        self.min_support = min_support

    def fit(self, X, y):
        df = X[[self.city_col, self.sector_col]].copy()
        df["_target"] = y.values if hasattr(y, "values") else y

        # Sector-level stats
        self.sector_stats_ = (
            df.groupby([self.city_col, self.sector_col])["_target"]
            .agg(["count", "median"])
            .reset_index()
        )

        # City-level fallback
        self.city_median_ = df.groupby(self.city_col)["_target"].median().to_dict()

        # Global fallback
        self.global_median_ = float(df["_target"].median())

        return self

    def transform(self, X):
        X = X.copy()

        merged = X.merge(
            self.sector_stats_,
            on=[self.city_col, self.sector_col],
            how="left",
        )

        # --- Vectorized priority chain (replaces slow row-wise apply) ---
        # Level 1: Sector median where support >= min_support
        has_support = merged["count"].notna() & (merged["count"] >= self.min_support)
        geo = np.where(has_support, merged["median"], np.nan)

        # Level 2: City median fallback
        city_vals = merged[self.city_col].map(self.city_median_)
        geo = np.where(np.isnan(geo.astype(float)), city_vals.values, geo)

        # Level 3: Global median last resort
        geo = np.where(pd.isna(geo), self.global_median_, geo)

        X["geo_median"] = geo.astype(float)

        # Drop consumed geo columns
        X = X.drop(columns=[self.city_col, self.sector_col])

        return X


# ---------------------------------------------------------------------------
# 4. Pipeline builder helpers
# ---------------------------------------------------------------------------


def _build_preprocessor(numeric_cols: list, categorical_pipeline: Pipeline) -> ColumnTransformer:
    """Shared ColumnTransformer builder used by both XGBoost and CatBoost pipelines."""
    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("winsor", Winsorizer()),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, list(CATEGORICAL_FEATURES)),
        ],
        remainder="drop",
    )


def _resolve_cols(df=None) -> tuple[list, list]:
    """Return (numeric_cols, categorical_cols) filtered by df presence."""
    requested_numeric = list(NUMERIC_FEATURES) + list(AMENITY_FEATURES)
    requested_categorical = list(CATEGORICAL_FEATURES)
    if df is not None:
        return (
            [c for c in requested_numeric if c in df.columns],
            [c for c in requested_categorical if c in df.columns],
        )
    return requested_numeric, requested_categorical


def build_feature_pipeline(model, df=None) -> Pipeline:
    """
    Assemble the full XGBoost prediction pipeline.

    Args:
        model: An sklearn-compatible estimator (e.g., XGBRegressor).
        df: Optional dataframe to filter features by presence.

    Returns:
        sklearn.pipeline.Pipeline with steps:
            feature_creator → geo_encoder → preprocessor → model
    """
    numeric_cols, _ = _resolve_cols(df)

    ohe_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessor = _build_preprocessor(numeric_cols, ohe_pipeline)

    return Pipeline(
        [
            ("feature_creator", FeatureCreator()),
            ("geo_encoder", GeoMedianEncoder()),
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def build_catboost_pipeline(model, df=None) -> Pipeline:
    """
    Assemble a CatBoost-compatible prediction pipeline.

    Identical to :func:`build_feature_pipeline` except the categorical
    sub-pipeline omits OneHotEncoder — CatBoost handles categoricals natively.

    Args:
        model: A CatBoostRegressor.
        df: Optional dataframe to filter features by presence.

    Returns:
        sklearn.pipeline.Pipeline with steps:
            feature_creator → geo_encoder → preprocessor → model
    """
    numeric_cols, _ = _resolve_cols(df)

    # No OHE — CatBoost accepts raw string categoricals via cat_features.
    passthrough_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ]
    )
    preprocessor = _build_preprocessor(numeric_cols, passthrough_pipeline)

    return Pipeline(
        [
            ("feature_creator", FeatureCreator()),
            ("geo_encoder", GeoMedianEncoder()),
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
