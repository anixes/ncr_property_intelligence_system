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
    "balcony",
    "floor",
    "log_area",
    "area_per_bedroom",
    "bathrooms_missing",
    "floor_missing",
    "geo_median",
]

CATEGORICAL_FEATURES = [
    "prop_type",
    "furnished",
    "facing",
]

# Binary amenity columns (treated as numeric passthrough)
AMENITY_FEATURES = [
    "pooja_room",
    "servant_room",
    "store_room",
    "pool",
    "gym",
    "lift",
    "parking",
    "vastu_compliant",
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
        floor_missing     — binary indicator
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
        X["floor_missing"] = X["floor"].isna().astype(int)

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

        def _resolve(row):
            # Level 1: sector median (if enough support)
            if pd.notna(row.get("count")) and row["count"] >= self.min_support:
                return row["median"]

            # Level 2: city median
            city_val = self.city_median_.get(row[self.city_col])
            if city_val is not None and pd.notna(city_val):
                return city_val

            # Level 3: global
            return self.global_median_

        X["geo_median"] = merged.apply(_resolve, axis=1)

        # Drop consumed geo columns — prevents accidental one-hot encoding
        X = X.drop(columns=[self.city_col, self.sector_col])

        return X


# ---------------------------------------------------------------------------
# 4. Pipeline builder
# ---------------------------------------------------------------------------


def build_feature_pipeline(model):
    """
    Assemble the full prediction pipeline.

    Args:
        model: An sklearn-compatible estimator (e.g., LGBMRegressor).

    Returns:
        sklearn.pipeline.Pipeline with steps:
            feature_creator → geo_encoder → preprocessor → model
    """
    numeric_cols = NUMERIC_FEATURES + AMENITY_FEATURES

    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("winsor", Winsorizer()),
        ]
    )

    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",  # safety: drop any unexpected columns
    )

    pipeline = Pipeline(
        [
            ("feature_creator", FeatureCreator()),
            ("geo_encoder", GeoMedianEncoder()),
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


def build_catboost_pipeline(model):
    """
    Assemble a prediction pipeline suitable for CatBoost.

    Identical to :func:`build_feature_pipeline` **except** the categorical
    sub-pipeline omits ``OneHotEncoder`` — it only imputes missing values
    with ``"Unknown"`` and passes raw strings through.  This preserves
    ``object`` dtype so CatBoost can use its native categorical handling
    via the ``cat_features`` parameter.

    Args:
        model: A CatBoostRegressor (or any estimator that accepts
               ``cat_features`` in its ``.fit()`` call).

    Returns:
        sklearn.pipeline.Pipeline with steps:
            feature_creator → geo_encoder → preprocessor → model
    """
    numeric_cols = NUMERIC_FEATURES + AMENITY_FEATURES

    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("winsor", Winsorizer()),
        ]
    )

    # No OneHotEncoder — CatBoost handles categoricals natively.
    # SimpleImputer returns a 2-D numpy array of dtype object, which
    # CatBoostRegressor accepts when indices are passed via cat_features.
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    pipeline = Pipeline(
        [
            ("feature_creator", FeatureCreator()),
            ("geo_encoder", GeoMedianEncoder()),
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline
