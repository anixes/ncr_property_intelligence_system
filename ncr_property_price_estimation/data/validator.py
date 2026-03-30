"""
V16 Validator — Skew-Aware Sanitization with Stage Tracking.

Validates raw extracted data, enforces semantic bounds, and handles
luxury-zone skew to avoid over-rejection in premium areas.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

# =============================================================================
# NCR INTELLIGENCE ENGINE (V16) - VALIDATION SERVICE
# =============================================================================


@dataclass
class StageCounter:
    """Tracks record counts across pipeline stages for observability."""

    raw: int = 0
    validated: int = 0
    enriched: int = 0
    fused: int = 0

    def report(self) -> dict[str, Any]:
        return {
            "raw": self.raw,
            "validated": self.validated,
            "enriched": self.enriched,
            "fused": self.fused,
            "validation_yield": round(self.validated / max(self.raw, 1), 3),
            "overall_yield": round(self.fused / max(self.raw, 1), 3),
        }


class ExtractionSemanticError(Exception):
    """Raised when extracted values fail basic common-sense checks."""

    pass


class ValidationService:
    """Industrial Validator with Skew-Aware Z-Score Logic (V16)."""

    # Semantic bounds for NCR real estate
    PRICE_MIN_BUY = 500_000  # 5 Lakh minimum for Buy
    PRICE_MIN_RENT = 5_000  # 5k minimum for Rent (prevents repo of deposits only)
    PRICE_MAX = 500_000_000  # 50 Crore cap
    AREA_MIN = 100  # 100 sqft minimum
    AREA_MAX = 50_000  # 50,000 sqft cap
    BHK_VALID = set(range(1, 11))  # 1 BHK to 10 BHK (Luxury Penthouses)

    def __init__(self):
        self.counter = StageCounter()
        self.rejection_log = []

    def validate_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run full validation pipeline on a raw batch."""
        self.counter.raw = len(df)

        # 1. Semantic Guards (V16)
        df = self._enforce_semantic_bounds(df)

        # 2. Skew-Aware Outlier Detection (V16 Formalized)
        df = self._skew_aware_filter(df)

        # 3. Quality Tagging
        df = self._tag_quality(df)

        self.counter.validated = len(df)
        return df

    def _enforce_semantic_bounds(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reject rows that fail basic common-sense checks."""
        # 0. Listing Mode Context
        is_rent = df.get("listing_mode", pd.Series("buy", index=df.index)).str.lower() == "rent"
        min_price = np.where(is_rent, self.PRICE_MIN_RENT, self.PRICE_MIN_BUY)

        mask = (
            (df["price"] >= min_price)
            & (df["price"] <= self.PRICE_MAX)
            & (df["area"] >= self.AREA_MIN)
            & (df["area"] <= self.AREA_MAX)
            & (df["bhk"].isin(self.BHK_VALID))
        )
        rejected = df[~mask]
        if len(rejected) > 0:
            self.rejection_log.extend(
                rejected[["listing_id", "price", "area", "bhk"]].to_dict("records")
            )
        return df[mask].copy()

    def _skew_aware_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Formalized Skew-Aware Z-Score Filter (V16).

        Logic:
        - Calculate skew_ratio = P95 / P50 for each H3 cell (or city).
        - If skew_ratio > 2.5 → luxury zone → relax threshold to 4.5.
        - Else → standard threshold of 3.0.
        """
        if "price" not in df.columns or len(df) < 10:
            return df

        group_col = "h3_res8" if "h3_res8" in df.columns else "city"

        def filter_group(group):
            if len(group) < 5:
                return group

            p50 = group["price"].quantile(0.50)
            p95 = group["price"].quantile(0.95)

            if p50 == 0:
                return group

            skew_ratio = p95 / p50
            zscore_threshold = 4.5 if skew_ratio > 2.5 else 3.0

            mean_price = group["price"].mean()
            std_price = group["price"].std()

            if std_price == 0:
                return group

            group["_zscore"] = abs((group["price"] - mean_price) / std_price)
            group["is_luxury_skew"] = skew_ratio > 2.5
            filtered = group[group["_zscore"] <= zscore_threshold].drop(columns=["_zscore"])
            return filtered

        return df.groupby(group_col, group_keys=False).apply(filter_group)

    def _tag_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tag data quality for downstream observability."""
        conditions = [
            df.get("area_uncertainty", pd.Series(0, index=df.index)) > 0.1,
            df.get("extraction_confidence", pd.Series(1.0, index=df.index)) < 0.8,
        ]

        df["quality_tag"] = "clean"
        for cond in conditions:
            df.loc[cond, "quality_tag"] = "degraded"

        return df

    def get_yield_report(self) -> dict[str, Any]:
        """Generate a yield report for observability."""
        return {
            "stage_counts": self.counter.report(),
            "rejections": len(self.rejection_log),
            "rejection_sample": self.rejection_log[:5],
        }
