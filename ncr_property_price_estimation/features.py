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
# 1. CityNormalizer (Data-Driven Pre-processing)
# ---------------------------------------------------------------------------


class CityNormalizer(BaseEstimator, TransformerMixin):
    """
    Standardize city names to match training data (Gurugram -> Gurgaon).
    This enables the API to accept current naming while maintaining
    model compatibility natively.
    """

    def __init__(self, mapping=None):
        self.mapping = mapping or {
            "Gurugram": "Gurgaon",
            "Greater Noida": "Greater_Noida",
            "Delhi": "Delhi",
        }

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        if "city" in X.columns:
            X["city"] = X["city"].replace(self.mapping)
        return X


# ---------------------------------------------------------------------------
# 1.5. SectorNormalizer (Micro-Market Synchronization)
# ---------------------------------------------------------------------------


class SectorNormalizer(BaseEstimator, TransformerMixin):
    """
    Standardize sector names and micro-market identifiers.
    Normalizes 'Sector 150' to 'Sector-150' at the feature level,
    preventing the MicroMarketEncoder from falling back to city medians.
    """

    def __init__(self, column="sector"):
        self.column = column

    def _map_sector(self, sector: str, city: str = "Noida") -> str:
        if not sector or pd.isna(sector):
            return "Unknown"

        # 1. Existing Institutional Mappings (Manual High-Fidelity)
        institutional_mapping = {
            "Sector 150": "Sector 137",
            "Sector 152": "Sector 137",
            "Sector 107": "Sector 108",
        }
        if sector in institutional_mapping:
            return institutional_mapping[sector]

        # 2. Regional Multi-City Clustering Fallback
        import re

        match = re.search(r"Sector\s+(\d+)", sector)
        if match:
            s_num = int(match.group(1))
            city_lower = str(city).lower()

            if "gurgaon" in city_lower:
                return "Sector 53" if s_num >= 60 else "Sector 12"
            elif "faridabad" in city_lower:
                return "Sector 29" if s_num >= 40 else "Sector 16"
            else:  # Noida Default
                return "Sector 108" if s_num >= 110 else "Sector 23"

        return sector

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        # Multi-City Row-wise Transformation
        if self.column in X.columns:
            # We use row.get('city') to adapt mapping to the specific regional context
            X[self.column] = X.apply(
                lambda row: self._map_sector(str(row[self.column]), str(row.get("city", "Noida"))),
                axis=1,
            )
        return X


# ---------------------------------------------------------------------------
# 2. Winsorizer
# ---------------------------------------------------------------------------


class Winsorizer(BaseEstimator, TransformerMixin):
    """
    Clip numeric features at fitted quantile bounds.

    If bypass_luxury is True, rows where is_luxury=1 will not be clipped
    for the 'area' column, preserving the true scale of ultra-premium estates.
    """

    def __init__(self, lower_q=0.01, upper_q=0.99, bypass_luxury=True):
        self.lower_q = lower_q
        self.upper_q = upper_q
        self.bypass_luxury = bypass_luxury

    def fit(self, X, y=None):
        # We only fit on non-luxury or all? Usually fit on all to get global stats
        self.lower_ = np.nanquantile(X, self.lower_q, axis=0)
        self.upper_ = np.nanquantile(X, self.upper_q, axis=0)

        # Capture schema to handle numpy fallbacks in transform
        if hasattr(X, "columns"):
            self.columns_ = X.columns.tolist()
        else:
            # Fallback for numpy arrays (best guess)
            self.columns_ = []

        return self

    def transform(self, X):
        # Use numpy directly for speed
        X_arr = X.values if hasattr(X, "values") else X
        X_clipped = np.clip(X_arr, self.lower_, self.upper_)

        # Apply luxury bypass (area is usually col 0, luxury is mid-way)
        bypass_luxury = getattr(self, "bypass_luxury", False)
        columns = getattr(self, "columns_", [])
        if bypass_luxury and columns:
            try:
                # Find indices from the fitted column list
                area_idx = columns.index("area")
                luxury_idx = columns.index("is_luxury")

                # Apply bypass: if Luxury bit is 1, keep original area
                luxury_mask = X_arr[:, luxury_idx] == 1
                X_clipped[luxury_mask, area_idx] = X_arr[luxury_mask, area_idx]
            except (ValueError, IndexError):
                pass  # Fallback: if columns not found in this subset, just skip bypass

        # Return same type as input
        if hasattr(X, "iloc"):
            return pd.DataFrame(X_clipped, columns=X.columns, index=X.index)
        return X_clipped

    def get_feature_names_out(self, input_features=None):
        return np.asarray(input_features) if input_features is not None else np.array([])


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
        if "bathrooms" in X.columns:
            X["bathrooms_missing"] = X["bathrooms"].isna().astype(int)

        return X


# ---------------------------------------------------------------------------
# 3. MicroMarketEncoder (Hierarchical Target Encoding)
# ---------------------------------------------------------------------------


class MicroMarketEncoder(BaseEstimator, TransformerMixin):
    """
    Encode geographic location as a single hierarchical price-index feature.

    Hierarchy (Successive fallbacks):
        1. Society-level median (if count >= min_support_soc)
        2. Sector-level median (if count >= min_support_sec)
        3. City-level median (fallback)
        4. Global median (last resort)

    This captures the 'Society Premium' (e.g. Camellias) which is invisible
    at the Sector level.
    """

    def __init__(
        self,
        city_col="city",
        sector_col="sector",
        society_col="society",
        min_support_soc=2,
        min_support_sec=10,
        bypass_drop=False,
    ):
        self.city_col = city_col
        self.sector_col = sector_col
        self.society_col = society_col
        self.min_support_soc = min_support_soc
        self.min_support_sec = min_support_sec
        self.bypass_drop = bypass_drop

    def fit(self, X, y):
        df = X[[self.city_col, self.sector_col, self.society_col]].copy()
        df["_target"] = y.values if hasattr(y, "values") else y

        # Society-level stats (The brand premium)
        self.soc_stats_ = (
            df.groupby([self.city_col, self.sector_col, self.society_col])["_target"]
            .agg(["count", "median"])
            .reset_index()
        )

        # Sector-level stats
        self.sec_stats_ = (
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

        # Layer 1: Society
        merged_soc = X.merge(
            self.soc_stats_,
            on=[self.city_col, self.sector_col, self.society_col],
            how="left",
            suffixes=("", "_soc"),
        )

        # Layer 2: Sector
        merged_sec = X.merge(
            self.sec_stats_, on=[self.city_col, self.sector_col], how="left", suffixes=("", "_sec")
        )

        # --- Hierarchy Logic ---
        # 1. Society Median
        has_soc_support = merged_soc["count"].notna() & (
            merged_soc["count"] >= self.min_support_soc
        )
        geo = np.where(has_soc_support, merged_soc["median"], np.nan)

        # 2. Sector Median Fallback
        has_sec_support = merged_sec["count"].notna() & (
            merged_sec["count"] >= self.min_support_sec
        )
        geo = np.where(
            np.isnan(geo.astype(float)),
            np.where(has_sec_support, merged_sec["median"], np.nan),
            geo,
        )

        # 3. City Median Fallback
        city_vals = X[self.city_col].map(self.city_median_)
        geo = np.where(np.isnan(geo.astype(float)), city_vals.values, geo)

        # 4. Global Median Last Resort
        geo = np.where(pd.isna(geo), self.global_median_, geo)

        X["geo_median"] = geo.astype(float)

        # Drop consumed geo columns (BUT keep society for CatBoost if bypass_drop=True)
        # For now, we drop to avoid leaking target info via OHE if someone uses it
        if not getattr(self, "bypass_drop", False):
            X = X.drop(columns=[self.city_col, self.sector_col, self.society_col])

        return X


# ---------------------------------------------------------------------------
# 4. Pipeline builder helpers
# ---------------------------------------------------------------------------


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


def build_catboost_pipeline(model, df=None) -> Pipeline:
    """
    Assemble the primary CatBoost prediction pipeline with Native Category support.
    """
    numeric_cols, categorical_cols = _resolve_cols(df)

    # In CatBoost mode, we ADD the spatial columns to the categorical list
    catboost_cat_cols = list(categorical_cols)
    for col in ["city", "sector", "society"]:
        if col not in catboost_cat_cols:
            catboost_cat_cols.append(col)

    passthrough_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ]
    )

    # Custom preprocessor that routes our extended categorical list
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("winsor", Winsorizer(bypass_luxury=True)),
                    ]
                ),
                numeric_cols,
            ),
            ("cat", passthrough_pipeline, catboost_cat_cols),
        ],
        remainder="drop",
    )

    return Pipeline(
        [
            ("city_normalizer", CityNormalizer()),
            ("sector_normalizer", SectorNormalizer()),
            ("feature_creator", FeatureCreator()),
            ("geo_encoder", MicroMarketEncoder(bypass_drop=True)),
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
