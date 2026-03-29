"""
Model Quality Gate tests. 

These tests run on the ACTUAL trained model artifacts and datasets.
Deployment should FAIL if these tests do not pass.

Highlight: R^2 > 0.40 threshold for both Sales and Rentals.
"""

import numpy as np
import pandas as pd
import pytest
from joblib import load
from pathlib import Path
from sklearn.metrics import r2_score

# ---------------------------------------------------------------------------
# Path resolution (relative to project root)
# ---------------------------------------------------------------------------
PROJ_ROOT = Path(__file__).resolve().parent.parent

MODELS_DIR = PROJ_ROOT / "models"
DATA_DIR = PROJ_ROOT / "data" / "model"

SALES_MODEL_PATH = MODELS_DIR / "sales" / "pipeline_sales.joblib"
RENTALS_MODEL_PATH = MODELS_DIR / "rentals" / "pipeline_rentals.joblib"

SALES_DATA_PATH = DATA_DIR / "model_sales.parquet"
RENTALS_DATA_PATH = DATA_DIR / "model_rentals.parquet"

# ---------------------------------------------------------------------------
# Shared Validation Logic
# ---------------------------------------------------------------------------

def validate_model_performance(model_path, data_path, threshold=0.40):
    """Common logic for R^2 quality gate."""
    if not model_path.exists():
        pytest.fail(f"Model artifact missing: {model_path}")
    if not data_path.exists():
        pytest.fail(f"Dataset missing: {data_path}")
        
    # Load model and data
    pipeline = load(model_path)
    df = pd.read_parquet(data_path)
    
    # Prepare X, y
    X = df.drop(columns=["price_per_sqft"])
    print(f"\n[DEBUG] X columns: {X.columns.tolist()}")
    y_true = np.log1p(df["price_per_sqft"])
    
    # Predict
    y_pred = pipeline.predict(X)
    
    # Metric
    r2 = r2_score(y_true, y_pred)
    
    assert r2 > threshold, f"Model R^2 ({r2:.4f}) is below threshold ({threshold})"
    return r2

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSalesModelQuality:
    @pytest.mark.skipif(not SALES_MODEL_PATH.exists(), reason="Sales model not found")
    def test_sales_r2_threshold(self):
        """GATE: Sales model R^2 must be > 0.40."""
        validate_model_performance(SALES_MODEL_PATH, SALES_DATA_PATH, threshold=0.40)

    @pytest.mark.skipif(not SALES_MODEL_PATH.exists(), reason="Sales model not found")
    def test_sales_predictions_are_reasonable(self):
        """Predictions should be within known log-scale ranges (7 to 14)."""
        pipeline = load(SALES_MODEL_PATH)
        df = pd.read_parquet(SALES_DATA_PATH).head(100)
        X = df.drop(columns=["price_per_sqft"])
        
        preds = pipeline.predict(X)
        
        assert np.all(np.isfinite(preds)), "Model produced non-finite predictions"
        # 7.0 (exp ~1100) to 14.0 (exp ~1.2M)
        assert preds.min() > 7.0, f"Min prediction {preds.min():.2f} too low"
        assert preds.max() < 14.0, f"Max prediction {preds.max():.2f} too high"


class TestRentalsModelQuality:
    @pytest.mark.skipif(not RENTALS_MODEL_PATH.exists(), reason="Rentals model not found")
    def test_rentals_r2_threshold(self):
        """GATE: Rentals model R^2 must be > 0.40."""
        validate_model_performance(RENTALS_MODEL_PATH, RENTALS_DATA_PATH, threshold=0.40)

    @pytest.mark.skipif(not RENTALS_MODEL_PATH.exists(), reason="Rentals model not found")
    def test_rentals_predictions_are_reasonable(self):
        """Predictions should be within known log-scale ranges (2 to 10)."""
        pipeline = load(RENTALS_MODEL_PATH)
        df = pd.read_parquet(RENTALS_DATA_PATH).head(100)
        X = df.drop(columns=["price_per_sqft"])
        
        preds = pipeline.predict(X)
        
        assert np.all(np.isfinite(preds)), "Model produced non-finite predictions"
        # 2.0 (exp ~6) to 10.0 (exp ~22k)
        assert preds.min() > 2.0, f"Min prediction {preds.min():.2f} too low"
        assert preds.max() < 10.0, f"Max prediction {preds.max():.2f} too high"
