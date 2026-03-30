"""
Data Contract Validation.

Verifies that the processed Parquet files match the expected schema
required by the CatBoost pipeline.

Highlight: Automated Schema verification during CI pipeline.
"""

from pathlib import Path

import pandas as pd
import pytest

PROJ_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJ_ROOT / "data" / "model"

REQUIRED_COLUMNS = [
    "area",
    "bedrooms",
    "bathrooms",
    "prop_type",
    "furnishing_status",
    "legal_status",
    "city",
    "sector",
    "society",
    "price_per_sqft",
]

# ---------------------------------------------------------------------------
# Sales Data Schema
# ---------------------------------------------------------------------------


class TestSalesDataSchema:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.path = DATA_DIR / "model_sales.parquet"
        if not self.path.exists():
            pytest.skip("Sales model dataset not found")
        self.df = pd.read_parquet(self.path)

    def test_required_columns_exist(self):
        """Check for core feature set."""
        for col in REQUIRED_COLUMNS:
            assert col in self.df.columns, f"Sales data missing column: {col}"

    def test_no_null_target(self):
        """Ensure price_per_sqft is fully populated."""
        assert self.df["price_per_sqft"].notna().all(), "Sales target has null values"

    def test_numeric_ranges(self):
        """Catch impossible values in area or price."""
        assert (self.df["area"] > 0).all(), "Found area <= 0 in Sales data"
        assert (self.df["price_per_sqft"] > 0).all(), "Found price <= 0 in Sales data"


# ---------------------------------------------------------------------------
# Rentals Data Schema
# ---------------------------------------------------------------------------


class TestRentalsDataSchema:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.path = DATA_DIR / "model_rentals.parquet"
        if not self.path.exists():
            pytest.skip("Rentals model dataset not found")
        self.df = pd.read_parquet(self.path)

    def test_required_columns_exist(self):
        """Check for core feature set."""
        for col in REQUIRED_COLUMNS:
            assert col in self.df.columns, f"Rentals data missing column: {col}"

    def test_no_null_target(self):
        """Ensure price_per_sqft is fully populated."""
        assert self.df["price_per_sqft"].notna().all(), "Rentals target has null values"
