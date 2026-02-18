"""
Train the property price estimation pipeline.

Reads model_v1.parquet, fits the sklearn Pipeline (feature engineering
+ LightGBM), evaluates on a hold-out set, and saves the trained
pipeline to models/pipeline_v1.joblib.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score
from lightgbm import LGBMRegressor
from joblib import dump

# Resolve project root from this file's location
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "model" / "model_v1.parquet"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Add source package to path so features module is importable by name
# (required for joblib/pickle serialization of custom transformers)
import sys
_pkg_dir = str(Path(__file__).resolve().parent.parent)
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)
from features import build_feature_pipeline


def main():
    # ------------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------------
    print("=" * 60)
    print("TRAINING PIPELINE")
    print("=" * 60)

    df = pd.read_parquet(DATA_PATH)
    print(f">> Loaded {len(df):,} rows from {DATA_PATH.name}")
    print(f">> Columns: {list(df.columns)}")

    # ------------------------------------------------------------------
    # 2. Separate features and target
    # ------------------------------------------------------------------
    X = df.drop(columns=["price_per_sqft"])
    y = np.log1p(df["price_per_sqft"])

    print(f">> Features: {list(X.columns)}")
    print(f">> Target: log1p(price_per_sqft)")

    # ------------------------------------------------------------------
    # 3. Train / test split
    # ------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f">> Train: {len(X_train):,} | Test: {len(X_test):,}")

    # ------------------------------------------------------------------
    # 4. Build and fit pipeline
    # ------------------------------------------------------------------
    model = LGBMRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=-1,
        random_state=42,
        verbose=-1,
    )

    pipeline = build_feature_pipeline(model)

    print("\n>> Fitting pipeline...")
    pipeline.fit(X_train, y_train)
    print(">> Pipeline fitted.")

    # ------------------------------------------------------------------
    # 5. Evaluate
    # ------------------------------------------------------------------
    y_pred = pipeline.predict(X_test)

    # Metrics on log scale
    rmse_log = root_mean_squared_error(y_test, y_pred)
    mae_log = mean_absolute_error(y_test, y_pred)
    r2_log = r2_score(y_test, y_pred)

    # Back-transform to original Rs/sqft scale
    y_test_orig = np.expm1(y_test)
    y_pred_orig = np.expm1(y_pred)

    rmse_orig = root_mean_squared_error(y_test_orig, y_pred_orig)
    mae_orig = mean_absolute_error(y_test_orig, y_pred_orig)
    r2_orig = r2_score(y_test_orig, y_pred_orig)

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"  {'Metric':<20} {'Log Scale':>12} {'Rs/sqft Scale':>14}")
    print(f"  {'-'*20} {'-'*12} {'-'*14}")
    print(f"  {'RMSE':<20} {rmse_log:>12.4f} {rmse_orig:>14,.0f}")
    print(f"  {'MAE':<20} {mae_log:>12.4f} {mae_orig:>14,.0f}")
    print(f"  {'R²':<20} {r2_log:>12.4f} {r2_orig:>14.4f}")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 6. Feature count verification
    # ------------------------------------------------------------------
    preprocessor = pipeline.named_steps["preprocessor"]
    feature_names = preprocessor.get_feature_names_out()
    print(f"\n>> Total features after preprocessing: {len(feature_names)}")
    print(f">> Feature names: {list(feature_names)}")

    # Safety check: sector/city should NOT appear
    for col in ["city", "sector"]:
        matches = [f for f in feature_names if col in f.lower()]
        if matches:
            print(f"   WARNING: '{col}' found in features: {matches}")
        else:
            print(f"   OK: '{col}' not in features")

    # ------------------------------------------------------------------
    # 7. Save pipeline
    # ------------------------------------------------------------------
    output_path = MODEL_DIR / "pipeline_v1.joblib"
    dump(pipeline, output_path)
    print(f"\n>> Pipeline saved to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
