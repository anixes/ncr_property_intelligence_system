import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from ncr_property_price_estimation.config import PROCESSED_DATA_DIR, PROJ_ROOT


@dataclass
class ModelDataConfig:
    mode: str  # 'sales' or 'rentals'
    input_path: Path
    output_path: Path
    bathroom_tolerance: int = 3
    drop_columns: tuple = (
        "url",
        "title",
        "scraped_at",
        "price_raw",
        "area_raw",
        "location",
        "society_name_raw",  # In case it exists
        "price",  # leaky: target = price / area
        "property_hash",
        "source_url",
        "geo_tier",
        "price_text",
        "area_text",
        "bhk_text",
        "geo_confidence",  # Diagnostic
        "local_zscore",  # Derived during enrichment, but noise for XGB
        "latitude",  # Captured in H3
        "longitude",  # Captured in H3
    )


def build_model_dataset(config: ModelDataConfig) -> None:
    print(f"\n[BUILDING MODEL DATASET: {config.mode.upper()}]")
    df = pd.read_parquet(config.input_path)
    print(f"  Input rows: {len(df):,}")

    # 1. Deduplicate
    if "property_hash" in df.columns:
        df = df.drop_duplicates(subset=["property_hash"])

    # 2. Scope: Drop Plots (Different Asset Class)
    if "prop_type" in df.columns:
        df = df[df["prop_type"] != "Plot"]

    # 3. Standardize Scraper-Missing Semantics
    if "prop_type" in df.columns:
        non_plot_mask = df["prop_type"] != "Plot"
        df.loc[non_plot_mask & (df["bedrooms"] == 0), "bedrooms"] = np.nan
        df.loc[non_plot_mask & (df["bathrooms"] == 0), "bathrooms"] = np.nan

    if "floor" in df.columns and "prop_type" in df.columns:
        apt_mask = df["prop_type"] == "Apartment"
        df.loc[apt_mask & (df["floor"] == 0), "floor"] = np.nan

    if "sector" in df.columns:
        df["sector"] = df["sector"].fillna("Unknown").astype(str)

    if "agent_name" in df.columns:
        df["agent_name"] = df["agent_name"].fillna("Unknown").astype(str)

    if "city" in df.columns:
        df["city"] = df["city"].fillna("Unknown").astype(str)

    # 4. Domain Filtering (Outlier Removal)
    if {"bathrooms", "bedrooms"}.issubset(df.columns):
        df = df[~(df["bathrooms"] > (df["bedrooms"] + config.bathroom_tolerance))]

    # Mode-Specific Outlier Filtering
    if config.mode == "sales":
        # Area < 250, Price < 10L
        df = df[(df["area"] >= 250) & (df["price"] >= 1000000)]
    elif config.mode == "rentals":
        # Area > 6000, Price > 5L
        df = df[(df["area"] <= 6000) & (df["price"] <= 500000)]

    df["price_per_sqft"] = df["price"] / df["area"]

    # 5. Multivariate Outlier Detection (Isolation Forest)
    # Detects structurally impossible combinations (e.g. 5 baths in 200 sqft)
    iso_features = ["area", "bedrooms", "bathrooms", "price_per_sqft"]
    # Drop rows missing these for ISO fit (Beds/Baths might have NaNs)
    iso_df = df[iso_features].dropna()
    if len(iso_df) > 100:
        iso = IsolationForest(contamination=0.01, random_state=42)
        anomalies = iso.fit_predict(iso_df)
        # Map back to original df
        df.loc[iso_df.index, "is_anomaly"] = anomalies
        # Filter (keep 1, drop -1)
        # Note: If a row was dropped for ISO fit, we keep it here for CatBoost to handle NaNs
        df = df[df["is_anomaly"] != -1].drop(columns=["is_anomaly"])
        print(
            f"  Multivariate outliers removed (Isolation Forest): {len(iso_df) - (anomalies == 1).sum():,}"
        )

    # 6. Drop Modeling-Irrelevant Columns
    df = df.drop(columns=list(config.drop_columns), errors="ignore")

    # --- Audit Friendly Reordering & Standardized Naming ---
    if "society_name" in df.columns:
        df.rename(columns={"society_name": "society"}, inplace=True)

    from ncr_property_price_estimation.features import (
        AMENITY_FEATURES,
        CATEGORICAL_FEATURES,
        NUMERIC_FEATURES,
    )

    PIPELINE_FEATURES = (
        ["society", "sector", "city"]
        + list(NUMERIC_FEATURES)
        + list(AMENITY_FEATURES)
        + list(CATEGORICAL_FEATURES)
    )
    for col in PIPELINE_FEATURES:
        if col not in df.columns and col != "geo_median":
            df[col] = 0 if col not in CATEGORICAL_FEATURES else "Unknown"

    audit_cols = [
        "listing_type",
        "society",
        "locality",
        "bedrooms",
        "bathrooms",
        "furnishing_status",
        "legal_status",
        "is_rera_registered",
        "is_servant_room",
        "is_study_room",
        "is_standalone",
        "is_owner_listing",
    ]
    existing_audit_cols = [c for c in audit_cols if c in df.columns]
    other_cols = [c for c in df.columns if c not in existing_audit_cols]
    df = df[existing_audit_cols + other_cols]

    # Also drop timestamp injected for enrichment
    if "timestamp" in df.columns:
        df = df.drop(columns=["timestamp"])

    # 6. Final Target Sanity Check
    assert df["price_per_sqft"].notna().all(), "Target price_per_sqft contains NaN"

    # 7. Save Model Dataset
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(config.output_path, index=False)

    print(f"  Final rows passed to Modeling: {len(df):,}")
    print(f"  Saved to: {config.output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["sales", "rentals"], required=True)
    args = parser.parse_args()

    in_file = f"{args.mode}_processed.parquet"
    out_file = f"model_{args.mode}.parquet"

    config = ModelDataConfig(
        mode=args.mode,
        input_path=PROCESSED_DATA_DIR / in_file,
        output_path=PROJ_ROOT / "data" / "model" / out_file,
    )
    build_model_dataset(config)
