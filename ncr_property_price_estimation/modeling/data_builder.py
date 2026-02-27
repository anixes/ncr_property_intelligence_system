from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# MODEL DATA CONFIG


@dataclass
class ModelDataConfig:
    input_path: str
    output_path: str
    bathroom_tolerance: int = 3  # domain rule
    drop_columns: tuple = (
        "url",
        "title",
        "scraped_at",
        "price_raw",
        "area_raw",
        "location",
        "locality",
        "society_name",
        "price",  # leaky: target = price / area
        "property_hash",  # row ID, not a feature
    )


# MODEL DATA BUILDER


def build_model_dataset(config: ModelDataConfig) -> None:
    """
    Convert schema-validated dataset into modeling-ready dataset.

    Responsibilities:
        - Deduplicate rows
        - Scope to built residential (drop plots)
        - Standardize scraper-missing semantics
        - Apply domain-level row filtering
        - Drop modeling-irrelevant columns
        - Save model_v1 dataset
    """

    df = pd.read_parquet(config.input_path)

    # 1. Deduplicate

    if "property_hash" in df.columns:
        df = df.drop_duplicates(subset=["property_hash"])

    # 2. Scope: Drop Plots (Different Asset Class)

    if "prop_type" in df.columns:
        df = df[df["prop_type"] != "Plot"]

    # 3. Standardize Scraper-Missing Semantics

    # Bedrooms & bathrooms:
    # Schema allows 0 (for plots), but plots are dropped.
    # For built properties, 0 indicates scraper-missing.
    if "prop_type" in df.columns:
        non_plot_mask = df["prop_type"] != "Plot"

        df.loc[non_plot_mask & (df["bedrooms"] == 0), "bedrooms"] = np.nan
        df.loc[non_plot_mask & (df["bathrooms"] == 0), "bathrooms"] = np.nan

    # Floor: treat 0 as missing only for Apartments
    if "floor" in df.columns and "prop_type" in df.columns:
        apt_mask = df["prop_type"] == "Apartment"
        df.loc[apt_mask & (df["floor"] == 0), "floor"] = np.nan

    # Sector: structural missing → category placeholder
    if "sector" in df.columns:
        df["sector"] = df["sector"].fillna("Unknown").astype(str)

    # City safety
    if "city" in df.columns:
        df["city"] = df["city"].fillna("Unknown").astype(str)

    # 4. Domain Filtering (Model-Specific Logic)

    if {"bathrooms", "bedrooms"}.issubset(df.columns):
        df = df[~(df["bathrooms"] > (df["bedrooms"] + config.bathroom_tolerance))]

    # 5. Drop Modeling-Irrelevant Columns

    df = df.drop(columns=list(config.drop_columns), errors="ignore")

    # 6. Final Target Sanity Check

    assert df["price_per_sqft"].notna().all(), (
        "Target price_per_sqft contains NaN after data_builder"
    )

    # 7. Save Model Dataset

    output_path = Path(config.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(output_path, index=False)

    print(f"Model dataset saved: {output_path}")
    print(f"Final rows: {len(df):,}")


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent.parent

    config = ModelDataConfig(
        input_path=str(PROJECT_ROOT / "data" / "processed" / "ncr_properties_cleaned.parquet"),
        output_path=str(PROJECT_ROOT / "data" / "model" / "model_v1.parquet"),
    )

    build_model_dataset(config)
