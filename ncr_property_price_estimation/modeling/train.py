"""
NCR Property Intelligence: 'Pure ML' Training Pipeline

Standardized CatBoost-only architecture with Optuna HPO and native
categorical feature support.

Workflow:
    1. Schema Healing     -- sensed & fixed missing features
    2. Sample Weighting   -- Luxury-Aware (3x weight for premium segments)
    3. Optuna HPO         -- Bayesian search for CatBoost (GroupKFold, pruning)
    4. CV Evaluation      -- 5-fold GroupKFold validation
    5. Final Fit & Export -- Full dataset training + MLflow Model Registry
    6. Feature Importance -- CatBoost Gain + Permutation Importance (n=10)

Validation:
    - Geographic leakage prevention: GroupKFold (sector as group key)
    - Weighted metrics: Priority given to top 5% value segments

Reads  data/model/model_{mode}.parquet
Saves  models/{mode}/pipeline_{mode}.joblib
       models/{mode}/feature_importance_gain.json
"""

import argparse
import json
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import optuna
import pandas as pd
from catboost import CatBoostRegressor
from joblib import dump
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold

# ── Reproducibility ───────────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)

# ── Paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# DATA_PATH and MODEL_DIR will be set dynamically in main()
MODEL_ROOT = PROJECT_ROOT / "models"

# Add source package to path so features module is importable by name
# (required for joblib/pickle serialization of custom transformers)
from ncr_property_price_estimation.config import (
    MLFLOW_TRACKING_URI,
)
from ncr_property_price_estimation.features import build_catboost_pipeline

# ── Grouping key ──────────────────────────────────────────────────────
GROUP_COL = "sector"

# ── Repeated evaluation config ────────────────────────────────────────
N_REPEATS = 5


# ======================================================================
# Helpers
# ======================================================================

METRIC_KEYS = [
    "RMSE (log)",
    "MAE (log)",
    "R2 (log)",
    "RMSE (Rs/sqft)",
    "MAE (Rs/sqft)",
    "R2 (Rs/sqft)",
]


def evaluate(y_true_log, y_pred_log):
    """Return metrics dict on both log-scale and original Rs/sqft scale."""
    rmse_log = np.sqrt(mean_squared_error(y_true_log, y_pred_log))
    mae_log = mean_absolute_error(y_true_log, y_pred_log)
    r2_log = r2_score(y_true_log, y_pred_log)

    y_true = np.expm1(y_true_log)
    y_pred = np.expm1(y_pred_log)

    return {
        "RMSE (log)": round(float(rmse_log), 4),
        "MAE (log)": round(float(mae_log), 4),
        "R2 (log)": round(float(r2_log), 4),
        "RMSE (Rs/sqft)": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 1),
        "MAE (Rs/sqft)": round(float(mean_absolute_error(y_true, y_pred)), 1),
        "R2 (Rs/sqft)": round(float(r2_score(y_true, y_pred)), 4),
    }


def print_comparison(results: dict):
    """Pretty-print a comparison table of baseline results."""
    header = (
        f"  {'Model':<20} {'RMSE(log)':>10} {'MAE(log)':>10} {'R2(log)':>10}"
        f" {'RMSE(Rs)':>12} {'MAE(Rs)':>12} {'R2(Rs)':>10}"
    )
    sep = f"  {'-' * 20} {'-' * 10} {'-' * 10} {'-' * 10} {'-' * 12} {'-' * 12} {'-' * 10}"
    print(header)
    print(sep)
    for name, m in results.items():
        print(
            f"  {name:<20}"
            f" {m['RMSE (log)']:>10.4f}"
            f" {m['MAE (log)']:>10.4f}"
            f" {m['R2 (log)']:>10.4f}"
            f" {m['RMSE (Rs/sqft)']:>12,.0f}"
            f" {m['MAE (Rs/sqft)']:>12,.0f}"
            f" {m['R2 (Rs/sqft)']:>10.4f}"
        )


def _to_native(obj):
    """Coerce numpy scalars to native Python types for JSON."""
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    return obj


def save_json(payload: dict, output_path: Path):
    """Write dict to JSON with UTF-8 encoding and numpy coercion."""
    output_path.write_text(
        json.dumps(_to_native(payload), indent=2),
        encoding="utf-8",
    )


# ======================================================================
# Phase 4 — Feature Importance
# ======================================================================


def export_feature_importance(pipeline, X_test, y_test, feature_names, model_dir):
    """Save model gain importance (or equivalent) and permutation importance to JSON."""
    model = pipeline.named_steps["model"]

    # ── 1. Gain Importance ────────────────────────────────────────────
    scores = model.get_feature_importance()
    gain_importance = {
        name: round(float(score), 4)
        for name, score in sorted(zip(feature_names, scores), key=lambda x: -x[1])
    }

    # ── 2. Permutation Importance ─────────────────────────────────────
    print(">> Calculating permutation importance (n_repeats=10)...")
    perm_result = permutation_importance(
        pipeline,
        X_test,
        y_test,
        n_repeats=10,
        random_state=SEED,
        scoring="neg_root_mean_squared_error",
        n_jobs=1,  # n_jobs=-1 fails on Windows with custom transformers
    )
    perm_importance = {
        name: round(float(imp), 6)
        for name, imp in sorted(
            zip(feature_names, perm_result.importances_mean),
            key=lambda x: -abs(x[1]),
        )
    }

    # ── 3. Save ───────────────────────────────────────────────────────
    payload = {
        "gain_importance": gain_importance,
        "permutation_importance_mean": perm_importance,
    }
    out_path = model_dir / "feature_importance_gain.json"
    save_json(payload, out_path)
    print(f">> Feature importance saved to: {out_path}")

    # Print top-10 gain
    print("\n  Top-10 features (gain):")
    for i, (name, score) in enumerate(list(gain_importance.items())[:10]):
        print(f"    {i + 1:>2}. {name:<30} {score:>12.1f}")

    return payload


# ======================================================================
# CatBoost Experiment  (Optuna-tuned, GroupKFold, two-stage fit)
# ======================================================================

# Reasonable defaults — used as fallback when Optuna is skipped.
CATBOOST_PARAMS: dict = {
    "iterations": 1000,
    "depth": 6,
    "learning_rate": 0.05,
    "l2_leaf_reg": 3.0,
    "random_seed": SEED,
    "verbose": 0,
    "early_stopping_rounds": 50,
}


def _get_cat_feature_indices(preprocessor) -> list[int]:
    """Return column indices whose name starts with ``cat__``.

    Relies on ``ColumnTransformer.get_feature_names_out()`` — the ``cat``
    transformer prefix is set in :func:`build_catboost_pipeline`.
    """
    feature_names = list(preprocessor.get_feature_names_out())
    return [i for i, col in enumerate(feature_names) if col.startswith("cat__")]


# ── Optuna CatBoost tuning ────────────────────────────────────────────


def create_catboost_objective(X_train: pd.DataFrame, y_train: pd.Series, groups_train: pd.Series):
    """Return an Optuna objective with GroupKFold CV and per-fold pruning."""

    def objective(trial: optuna.Trial) -> float:
        params = {
            "iterations": trial.suggest_int("iterations", 300, 2000),
            "depth": trial.suggest_int("depth", 4, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1.0, 10.0, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bylevel": trial.suggest_float("colsample_bylevel", 0.5, 1.0),
            "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 1, 30),
            "random_seed": SEED,
            "verbose": 0,
            "early_stopping_rounds": 50,
        }

        gkf = GroupKFold(n_splits=3)
        fold_scores: list[float] = []

        for fold_idx, (tr_idx, val_idx) in enumerate(gkf.split(X_train, y_train, groups_train)):
            X_tr, X_val = X_train.iloc[tr_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train.iloc[tr_idx], y_train.iloc[val_idx]

            cb_model = CatBoostRegressor(**params)
            pipeline = build_catboost_pipeline(cb_model, df=X_tr)

            # Two-stage fit: preprocess → CatBoost with cat_features
            preprocess_steps = pipeline[:-1]
            X_tr_t = preprocess_steps.fit_transform(X_tr, y_tr)
            X_val_t = preprocess_steps.transform(X_val)

            cat_indices = _get_cat_feature_indices(pipeline.named_steps["preprocessor"])

            cb_model.fit(
                X_tr_t,
                y_tr,
                eval_set=(X_val_t, y_val),
                cat_features=cat_indices,
                use_best_model=True,
            )

            y_pred = cb_model.predict(X_val_t)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            fold_scores.append(rmse)

            # Report running mean for pruning
            trial.report(np.mean(fold_scores), fold_idx)
            if trial.should_prune():
                raise optuna.TrialPruned()

        return float(np.mean(fold_scores))

    return objective


def run_catboost_optuna(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    groups_train: pd.Series,
    model_dir: Path,  # Added model_dir parameter
    n_trials: int = 50,
) -> dict:
    """Run Optuna study for CatBoost with GroupKFold.  SQLite backend."""
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    storage_url = f"sqlite:///{model_dir / 'optuna_catboost.db'}"

    study = optuna.create_study(
        direction="minimize",
        study_name="catboost_hpo",
        sampler=optuna.samplers.TPESampler(seed=SEED),
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=1),
        storage=storage_url,
        load_if_exists=True,
    )
    study.optimize(
        create_catboost_objective(X_train, y_train, groups_train),
        n_trials=n_trials,
        show_progress_bar=True,
    )

    n_pruned = len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])
    n_complete = len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])

    print(f"\n  Trials completed: {n_complete} | pruned: {n_pruned}")
    print(f"  Best trial RMSE (grouped 3-fold CV): {study.best_value:.4f}")
    print("  Best params:")
    for k, v in study.best_params.items():
        print(f"    {k}: {v}")

    return study.best_params


def main():
    parser = argparse.ArgumentParser(
        description="NCR Property Intelligence: CatBoost-Only Training"
    )
    parser.add_argument("--mode", type=str, choices=["sales", "rentals"], default="sales")
    parser.add_argument(
        "--trials", type=int, default=1, help="Optuna trials. Use 1 for quick-train."
    )
    args = parser.parse_args()

    mode = args.mode
    data_path = PROJECT_ROOT / "data" / "model" / f"model_{mode}.parquet"
    model_dir = MODEL_ROOT / mode
    model_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    if not data_path.exists():
        raise FileNotFoundError(f"Missing training data: {data_path}")

    df = pd.read_parquet(data_path)
    print("=" * 72)
    print(f"🚀 PURE-ML PIPELINE: {mode.upper()}")
    print("=" * 72)
    print(f">> Loaded {len(df):,} rows from {data_path.name}")

    # 2. Schema Healing
    from ncr_property_price_estimation.features import (
        AMENITY_FEATURES,
        CATEGORICAL_FEATURES,
        NUMERIC_FEATURES,
    )

    if "society_name" in df.columns:
        df.rename(columns={"society_name": "society"}, inplace=True)

    expected_cols = (
        ["society", "sector", "city"]
        + list(NUMERIC_FEATURES)
        + list(AMENITY_FEATURES)
        + list(CATEGORICAL_FEATURES)
    )
    for col in expected_cols:
        if col not in df.columns and col != "geo_median":
            df[col] = 0 if col not in CATEGORICAL_FEATURES else "Unknown"

    # 3. Features / Target / Weighting
    X = df.drop(columns=["price_per_sqft"])
    y = np.log1p(df["price_per_sqft"])
    groups = X[GROUP_COL]

    # Sample Weighting (Luxury Accuracy)
    sample_weights = np.ones(len(df))
    if "is_luxury" in df.columns:
        sample_weights = np.where(df["is_luxury"] == 1, 3.0, 1.0)
    price_threshold = df["price_per_sqft"].quantile(0.95)
    sample_weights = np.where(
        df["price_per_sqft"] > price_threshold, sample_weights * 1.5, sample_weights
    )

    # 4. MLflow Setup
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(f"ncr-property-{mode}")

    # Safe-Start: Ensure no lingering runs
    try:
        if mlflow.active_run():
            mlflow.end_run()
    except Exception:
        pass

    with mlflow.start_run(run_name=f"catboost-optuna-{mode}") as run:
        print(f"\n>> MLflow run ID: {run.info.run_id}")

        # PHASE 1: Optuna HPO (if requested)
        if args.trials > 1:
            print(f"\n>> OPTUNA TUNING ({args.trials} trials, GroupKFold)")
            best_params = run_catboost_optuna(X, y, groups, model_dir, n_trials=args.trials)
            hparams = {
                **best_params,
                "random_seed": SEED,
                "verbose": 0,
                "early_stopping_rounds": 50,
            }
        else:
            print("\n>> Using default CatBoost parameters.")
            hparams = {
                **CATBOOST_PARAMS,
                "random_seed": SEED,
                "verbose": 0,
                "early_stopping_rounds": 50,
            }

        # PHASE 2: Cross-Validation
        print("\n>> 5-FOLD GROUPED CV EVALUATION")
        gkf = GroupKFold(n_splits=5)
        fold_r2, fold_rmse = [], []

        for fold_idx, (tr_idx, val_idx) in enumerate(gkf.split(X, y, groups), start=1):
            X_tr, X_val = X.iloc[tr_idx], X.iloc[val_idx]
            y_tr, y_val = y.iloc[tr_idx], y.iloc[val_idx]
            w_tr = sample_weights[tr_idx]

            cb_model = CatBoostRegressor(**hparams)
            pipeline = build_catboost_pipeline(cb_model, df=X_tr)

            # Two-stage fit for cat_features
            prep = pipeline[:-1]
            X_tr_t = prep.fit_transform(X_tr, y_tr)
            X_val_t = prep.transform(X_val)
            cat_idx = _get_cat_feature_indices(pipeline.named_steps["preprocessor"])

            cb_model.fit(
                X_tr_t,
                y_tr,
                sample_weight=w_tr,
                eval_set=(X_val_t, y_val),
                cat_features=cat_idx,
                use_best_model=True,
            )

            y_pred = cb_model.predict(X_val_t)
            fold_r2.append(r2_score(y_val, y_pred))
            fold_rmse.append(np.sqrt(mean_squared_error(y_val, y_pred)))
            print(f"  Fold {fold_idx}/5 | R²: {fold_r2[-1]:.4f} | RMSE: {fold_rmse[-1]:.4f}")

        # Final metrics
        metrics = {"mean_cv_r2": float(np.mean(fold_r2)), "mean_cv_rmse": float(np.mean(fold_rmse))}

        # PHASE 3: Final Fit & Export
        print("\n>> Fitting final model on full dataset...")
        final_model = CatBoostRegressor(
            **{k: v for k, v in hparams.items() if k != "early_stopping_rounds"}
        )
        final_pipeline = build_catboost_pipeline(final_model, df=X)

        prep = final_pipeline[:-1]
        X_full_t = prep.fit_transform(X, y)
        cat_idx = _get_cat_feature_indices(final_pipeline.named_steps["preprocessor"])
        final_model.fit(X_full_t, y, cat_features=cat_idx)

        final_pipeline.steps[-1] = ("model", final_model)

        # Feature Importance
        feature_names = list(final_pipeline.named_steps["preprocessor"].get_feature_names_out())
        export_feature_importance(
            final_pipeline, X.head(100), y.head(100), feature_names, model_dir
        )

        # Log & Save
        mlflow.log_params(hparams)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            sk_model=final_pipeline,
            artifact_path="catboost_pipeline",
            registered_model_name=f"property-estimator-{mode}",
        )

        pipeline_path = model_dir / f"pipeline_{mode}.joblib"
        dump(final_pipeline, pipeline_path)

        # Save evaluation results for reporting (Pure-ML mode)
        results_payload = {
            "mode": mode,
            "seed": SEED,
            "mlflow_run_id": run.info.run_id,
            "cv_metrics": {
                "mean_r2": metrics["mean_cv_r2"],
                "mean_rmse_log": metrics["mean_cv_rmse"],
                "folds": {
                    f"fold_{i + 1}": {"r2": r2, "rmse": rmse}
                    for i, (r2, rmse) in enumerate(zip(fold_r2, fold_rmse))
                },
            },
            "best_params": hparams,
        }
        save_json(results_payload, model_dir / "experiment_results.json")

        print(f"\n>> SUCCESS: Model saved to {pipeline_path}")
        print(">> Pure ML CatBoost-Only Pipeline Complete.")


if __name__ == "__main__":
    main()
