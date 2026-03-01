"""
Train the property price estimation pipeline.

Workflow:
    1. Baseline comparison  -- Ridge (scaled), RandomForest, LightGBM, XGBoost
    2. Optuna-tuned XGBoost -- 50-trial Bayesian search (GroupKFold CV, pruning)
    3. Final evaluation     -- Repeated GroupShuffleSplit (5 repeats, refit each)
    4. Feature importance   -- Gain importance + permutation importance

Validation:
    - Train/test split via GroupShuffleSplit (sector as group key)
    - CV inside Optuna via GroupKFold (sector as group key)
    - Final metrics via 5-repeat grouped resampling (mean +/- std)
    - Prevents geographic leakage at every stage

Note on time-awareness:
    scraped_at is intentionally dropped in data_builder.py to prevent
    temporal leakage.  This model is cross-sectional, not time-aware.

Reads  data/model/model_v1.parquet
Saves  models/pipeline_v1.joblib
       models/experiment_results.json
       models/feature_importance_gain.json
"""

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
from lightgbm import LGBMRegressor
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import make_pipeline as _make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

# ── Reproducibility ───────────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)

# ── Paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "model" / "model_v1.parquet"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Add source package to path so features module is importable by name
# (required for joblib/pickle serialization of custom transformers)
from ncr_property_price_estimation.config import (
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_MODEL_NAME,
    MLFLOW_TRACKING_URI,
)
from ncr_property_price_estimation.features import build_catboost_pipeline, build_feature_pipeline

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
# Phase 1 — Baseline Comparison
# ======================================================================


def get_baselines():
    """Return dict of baseline models.

    Ridge is wrapped with StandardScaler since the numeric preprocessing
    (imputer + winsorizer) does not scale -- tree models don't need it,
    but Ridge's L2 penalty is scale-dependent.
    """
    return {
        "Ridge": _make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "RandomForest": RandomForestRegressor(
            n_estimators=300,
            max_depth=15,
            random_state=SEED,
            n_jobs=-1,
        ),
        "LightGBM": LGBMRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=-1,
            random_state=SEED,
            verbose=-1,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            random_state=SEED,
            verbosity=0,
        ),
    }


def run_baselines(X_train, y_train, X_test, y_test):
    """Train every baseline, evaluate, and return results dict."""
    results = {}
    for name, model in get_baselines().items():
        print(f"  Training {name}...")
        pipe = build_feature_pipeline(model)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        results[name] = evaluate(y_test, y_pred)
    return results


# ======================================================================
# Phase 2 — Optuna XGBoost Tuning  (GroupKFold + fold-level pruning)
# ======================================================================


def create_objective(X_train, y_train, groups_train):
    """Return an Optuna objective with grouped CV and per-fold pruning."""

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 200, 1500),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "random_state": SEED,
            "verbosity": 0,
        }

        gkf = GroupKFold(n_splits=3)
        fold_scores = []

        for fold_idx, (tr_idx, val_idx) in enumerate(gkf.split(X_train, y_train, groups_train)):
            X_tr = X_train.iloc[tr_idx]
            X_val = X_train.iloc[val_idx]
            y_tr = y_train.iloc[tr_idx]
            y_val = y_train.iloc[val_idx]

            pipe = build_feature_pipeline(XGBRegressor(**params))
            pipe.fit(X_tr, y_tr)

            y_pred = pipe.predict(X_val)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            fold_scores.append(rmse)

            # Report running mean for pruning
            trial.report(np.mean(fold_scores), fold_idx)
            if trial.should_prune():
                raise optuna.TrialPruned()

        return np.mean(fold_scores)

    return objective


def run_optuna(X_train, y_train, groups_train, n_trials=50):
    """Run Optuna study with GroupKFold.  SQLite backend for crash safety."""
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    storage_url = f"sqlite:///{MODEL_DIR / 'optuna.db'}"

    study = optuna.create_study(
        direction="minimize",
        study_name="xgb_hpo",
        sampler=optuna.samplers.TPESampler(seed=SEED),
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=1),
        storage=storage_url,
        load_if_exists=True,
    )
    study.optimize(
        create_objective(X_train, y_train, groups_train),
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


# ======================================================================
# Phase 3 — Repeated Grouped Evaluation
# ======================================================================


def repeated_grouped_eval(pipeline_template, X, y, groups, n_repeats=N_REPEATS):
    """Evaluate via repeated GroupShuffleSplit.  Refits a fresh clone each repeat.

    Returns:
        all_metrics: list of metric dicts (one per repeat)
        summary:     {"mean": {...}, "std": {...}}
    """
    all_metrics = []

    for i in range(n_repeats):
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED + i)
        tr_idx, te_idx = next(gss.split(X, y, groups))

        X_tr, X_te = X.iloc[tr_idx], X.iloc[te_idx]
        y_tr, y_te = y.iloc[tr_idx], y.iloc[te_idx]

        pipe = clone(pipeline_template)
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_te)

        metrics = evaluate(y_te, y_pred)
        all_metrics.append(metrics)
        print(f"  Repeat {i + 1}/{n_repeats}  R2(log)={metrics['R2 (log)']:.4f}")

    # Aggregate
    summary = {"mean": {}, "std": {}}
    for key in METRIC_KEYS:
        vals = [m[key] for m in all_metrics]
        summary["mean"][key] = round(float(np.mean(vals)), 4)
        summary["std"][key] = round(float(np.std(vals)), 4)

    return all_metrics, summary


# ======================================================================
# Phase 4 — Feature Importance
# ======================================================================


def export_feature_importance(pipeline, X_test, y_test, feature_names):
    """Export XGBoost gain importance and sklearn permutation importance."""

    # ── 1. Gain importance (XGBoost native) ───────────────────────────
    model_step = pipeline.named_steps["model"]

    # Unwrap if model_step is itself a sub-pipeline (e.g. Ridge)
    if hasattr(model_step, "get_booster"):
        booster = model_step.get_booster()
        raw_gain = booster.get_score(importance_type="gain")

        # Map booster feature names (f0, f1, ...) to real names
        booster_names = booster.feature_names
        if booster_names is None:
            booster_names = [f"f{i}" for i in range(len(feature_names))]

        name_map = dict(zip(booster_names, feature_names))
        gain_importance = {
            name_map.get(k, k): round(v, 4)
            for k, v in sorted(raw_gain.items(), key=lambda x: -x[1])
        }
    else:
        gain_importance = {}

    # ── 2. Permutation importance (model-agnostic) ────────────────────
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
    out_path = MODEL_DIR / "feature_importance_gain.json"
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
            pipeline = build_catboost_pipeline(cb_model)

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
    n_trials: int = 50,
) -> dict:
    """Run Optuna study for CatBoost with GroupKFold.  SQLite backend."""
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    storage_url = f"sqlite:///{MODEL_DIR / 'optuna_catboost.db'}"

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


# ── Main CatBoost entry point ─────────────────────────────────────────


def train_catboost(
    df: pd.DataFrame,
    params: dict | None = None,
    n_trials: int = 50,
) -> tuple[object, dict]:
    """Train a CatBoostRegressor with Optuna tuning, GroupKFold CV, and MLflow.

    Workflow:
        1. Optuna HPO  — ``n_trials`` Bayesian search (GroupKFold, pruning)
        2. Evaluate     — 5-fold GroupKFold CV with best params
        3. Final fit    — retrain on full data
        4. MLflow log   — params, metrics, pipeline artifact

    Args:
        df: Raw modelling DataFrame (must contain ``price_per_sqft``).
        params: Optional CatBoost hyperparameters.  If provided, Optuna
                tuning is **skipped** and these params are used directly.
        n_trials: Number of Optuna trials (ignored when *params* given).

    Returns:
        (fitted_pipeline, metrics_dict) where *fitted_pipeline* is
        trained on the full dataset and *metrics_dict* contains the
        mean / std of CV R² and RMSE (log-scale).
    """
    # ── Separate features / target ────────────────────────────────────
    X = df.drop(columns=["price_per_sqft"])
    y = np.log1p(df["price_per_sqft"])
    groups = X[GROUP_COL]

    print("=" * 72)
    print("CATBOOST EXPERIMENT  (Optuna-tuned)")
    print("=" * 72)
    print(f">> Rows: {len(X):,}")

    # ── Phase 1: Optuna tuning (or use provided params) ───────────────
    if params is not None:
        hparams = {**CATBOOST_PARAMS, **params}
        print(">> Using provided hyperparameters (Optuna skipped)")
    else:
        print(f"\n>> OPTUNA TUNING  ({n_trials} trials, GroupKFold)")
        print("-" * 72)
        best_params = run_catboost_optuna(X, y, groups, n_trials=n_trials)
        hparams = {
            **best_params,
            "random_seed": SEED,
            "verbose": 0,
            "early_stopping_rounds": 50,
        }

    print(f"\n>> Hyperparameters: {hparams}")

    # ── Phase 2: GroupKFold evaluation with best params ───────────────
    print("\n>> GROUPED CV EVALUATION  (5-fold)")
    print("-" * 72)
    gkf = GroupKFold(n_splits=5)

    fold_r2: list[float] = []
    fold_rmse: list[float] = []

    for fold_idx, (tr_idx, val_idx) in enumerate(gkf.split(X, y, groups), start=1):
        X_tr, X_val = X.iloc[tr_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[tr_idx], y.iloc[val_idx]

        cb_model = CatBoostRegressor(**hparams)
        pipeline = build_catboost_pipeline(cb_model)

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
        r2 = r2_score(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))

        fold_r2.append(float(r2))
        fold_rmse.append(float(rmse))
        print(f"  Fold {fold_idx}/5  R²={r2:.4f}  RMSE={rmse:.4f}")

    mean_r2 = float(np.mean(fold_r2))
    std_r2 = float(np.std(fold_r2))
    mean_rmse = float(np.mean(fold_rmse))
    std_rmse = float(np.std(fold_rmse))

    print(f"\n  CV R² (log):   {mean_r2:.4f} ± {std_r2:.4f}")
    print(f"  CV RMSE (log): {mean_rmse:.4f} ± {std_rmse:.4f}")

    # ── Phase 3: Train final model on full data ───────────────────────
    print("\n>> Fitting final model on full dataset...")

    final_model = CatBoostRegressor(**hparams)
    final_pipeline = build_catboost_pipeline(final_model)

    preprocess_steps = final_pipeline[:-1]
    X_full_t = preprocess_steps.fit_transform(X, y)
    cat_indices = _get_cat_feature_indices(final_pipeline.named_steps["preprocessor"])

    # No eval_set for final model — disable early stopping
    final_hparams = {k: v for k, v in hparams.items() if k != "early_stopping_rounds"}
    final_model = CatBoostRegressor(**final_hparams)
    final_model.fit(X_full_t, y, cat_features=cat_indices)

    # Replace the model step in the pipeline with the fully-trained one
    final_pipeline.steps[-1] = ("model", final_model)

    # ── Phase 4: MLflow logging ───────────────────────────────────────
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    metrics = {
        "mean_cv_r2_log": round(mean_r2, 4),
        "std_cv_r2_log": round(std_r2, 4),
        "mean_cv_rmse_log": round(mean_rmse, 4),
        "std_cv_rmse_log": round(std_rmse, 4),
    }

    with mlflow.start_run(run_name="catboost-optuna") as run:
        mlflow.log_param("model_type", "catboost")
        mlflow.log_params({k: v for k, v in hparams.items() if k != "verbose"})
        mlflow.log_metrics(metrics)

        mlflow.sklearn.log_model(
            sk_model=final_pipeline,
            artifact_path="catboost_pipeline",
        )

        print(f"\n>> MLflow run ID: {run.info.run_id}")

    print(">> CatBoost experiment complete.")
    print("=" * 72)

    return final_pipeline, metrics


# ======================================================================
# LightGBM Experiment  (Optuna-tuned, GroupKFold)
# ======================================================================

# Reasonable defaults — used as fallback when Optuna is skipped.
LGBM_PARAMS: dict = {
    "n_estimators": 500,
    "max_depth": -1,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_alpha": 0.0,
    "reg_lambda": 0.0,
    "random_state": SEED,
    "verbose": -1,
}


def create_lgbm_objective(X_train: pd.DataFrame, y_train: pd.Series, groups_train: pd.Series):
    """Return an Optuna objective for LightGBM with GroupKFold CV."""

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 200, 2000),
            "num_leaves": trial.suggest_int("num_leaves", 16, 128),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
            "random_state": SEED,
            "verbose": -1,
        }

        gkf = GroupKFold(n_splits=3)
        fold_scores: list[float] = []

        for fold_idx, (tr_idx, val_idx) in enumerate(gkf.split(X_train, y_train, groups_train)):
            X_tr, X_val = X_train.iloc[tr_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train.iloc[tr_idx], y_train.iloc[val_idx]

            pipe = build_feature_pipeline(LGBMRegressor(**params))
            pipe.fit(X_tr, y_tr)

            y_pred = pipe.predict(X_val)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            fold_scores.append(rmse)

            trial.report(np.mean(fold_scores), fold_idx)
            if trial.should_prune():
                raise optuna.TrialPruned()

        return float(np.mean(fold_scores))

    return objective


def run_lgbm_optuna(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    groups_train: pd.Series,
    n_trials: int = 50,
) -> dict:
    """Run Optuna study for LightGBM with GroupKFold.  SQLite backend."""
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    storage_url = f"sqlite:///{MODEL_DIR / 'optuna_lgbm.db'}"

    study = optuna.create_study(
        direction="minimize",
        study_name="lgbm_hpo",
        sampler=optuna.samplers.TPESampler(seed=SEED),
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=1),
        storage=storage_url,
        load_if_exists=True,
    )
    study.optimize(
        create_lgbm_objective(X_train, y_train, groups_train),
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


# ── Main LightGBM entry point ─────────────────────────────────────────


def train_lightgbm(
    df: pd.DataFrame,
    params: dict | None = None,
    n_trials: int = 50,
) -> tuple[object, dict]:
    """Train a LGBMRegressor with Optuna tuning, GroupKFold CV, and MLflow.

    Workflow mirrors :func:`train_catboost` but uses the standard
    :func:`build_feature_pipeline` (OneHotEncoded categoricals) — no
    two-stage fit required.

    Args:
        df: Raw modelling DataFrame (must contain ``price_per_sqft``).
        params: Optional LightGBM hyperparameters.  If provided, Optuna
                tuning is **skipped** and these params are used directly.
        n_trials: Number of Optuna trials (ignored when *params* given).

    Returns:
        (fitted_pipeline, metrics_dict)
    """
    # ── Separate features / target ────────────────────────────────────
    X = df.drop(columns=["price_per_sqft"])
    y = np.log1p(df["price_per_sqft"])
    groups = X[GROUP_COL]

    print("=" * 72)
    print("LIGHTGBM EXPERIMENT  (Optuna-tuned)")
    print("=" * 72)
    print(f">> Rows: {len(X):,}")

    # ── Phase 1: Optuna tuning (or use provided params) ───────────────
    if params is not None:
        hparams = {**LGBM_PARAMS, **params}
        print(">> Using provided hyperparameters (Optuna skipped)")
    else:
        print(f"\n>> OPTUNA TUNING  ({n_trials} trials, GroupKFold)")
        print("-" * 72)
        best_params = run_lgbm_optuna(X, y, groups, n_trials=n_trials)
        hparams = {**best_params, "random_state": SEED, "verbose": -1}

    print(f"\n>> Hyperparameters: {hparams}")

    # ── Phase 2: GroupKFold evaluation with best params ───────────────
    print("\n>> GROUPED CV EVALUATION  (5-fold)")
    print("-" * 72)
    gkf = GroupKFold(n_splits=5)

    fold_r2: list[float] = []
    fold_rmse: list[float] = []

    for fold_idx, (tr_idx, val_idx) in enumerate(gkf.split(X, y, groups), start=1):
        X_tr, X_val = X.iloc[tr_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[tr_idx], y.iloc[val_idx]

        pipe = build_feature_pipeline(LGBMRegressor(**hparams))
        pipe.fit(X_tr, y_tr)

        y_pred = pipe.predict(X_val)
        r2 = r2_score(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))

        fold_r2.append(float(r2))
        fold_rmse.append(float(rmse))
        print(f"  Fold {fold_idx}/5  R²={r2:.4f}  RMSE={rmse:.4f}")

    mean_r2 = float(np.mean(fold_r2))
    std_r2 = float(np.std(fold_r2))
    mean_rmse = float(np.mean(fold_rmse))
    std_rmse = float(np.std(fold_rmse))

    print(f"\n  CV R² (log):   {mean_r2:.4f} ± {std_r2:.4f}")
    print(f"  CV RMSE (log): {mean_rmse:.4f} ± {std_rmse:.4f}")

    # ── Phase 3: Train final model on full data ───────────────────────
    print("\n>> Fitting final pipeline on full dataset...")
    final_pipeline = build_feature_pipeline(LGBMRegressor(**hparams))
    final_pipeline.fit(X, y)

    # ── Phase 4: MLflow logging ───────────────────────────────────────
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    metrics = {
        "mean_cv_r2_log": round(mean_r2, 4),
        "std_cv_r2_log": round(std_r2, 4),
        "mean_cv_rmse_log": round(mean_rmse, 4),
        "std_cv_rmse_log": round(std_rmse, 4),
    }

    with mlflow.start_run(run_name="lgbm-optuna") as run:
        mlflow.log_param("model_type", "lightgbm")
        mlflow.log_params({k: v for k, v in hparams.items() if k != "verbose"})
        mlflow.log_metrics(metrics)

        mlflow.sklearn.log_model(
            sk_model=final_pipeline,
            artifact_path="lgbm_pipeline",
        )

        print(f"\n>> MLflow run ID: {run.info.run_id}")

    print(">> LightGBM experiment complete.")
    print("=" * 72)

    return final_pipeline, metrics


# ======================================================================
# Main
# ======================================================================


def main():
    print("=" * 72)
    print("TRAINING PIPELINE -- Multi-Model + Optuna (grouped validation)")
    print("=" * 72)

    # ── MLflow setup ──────────────────────────────────────────────────
    # MLFLOW_TRACKING_URI is already a file:/// URI (cross-OS safe).
    # Override with env var MLFLOW_TRACKING_URI for Docker / CI.
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    print(f">> MLflow tracking URI : {MLFLOW_TRACKING_URI}")
    print(f">> MLflow experiment   : {MLFLOW_EXPERIMENT_NAME}")

    # ── 1. Load data ──────────────────────────────────────────────────
    df = pd.read_parquet(DATA_PATH)
    print(f">> Loaded {len(df):,} rows from {DATA_PATH.name}")

    # ── 2. Separate features / target ─────────────────────────────────
    X = df.drop(columns=["price_per_sqft"])
    y = np.log1p(df["price_per_sqft"])

    print(f">> Features: {list(X.columns)}")
    print(">> Target: log1p(price_per_sqft)")

    # ── 3. Grouped train / test split ─────────────────────────────────
    groups = X[GROUP_COL]

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    groups_train = groups.iloc[train_idx]

    n_sectors_train = groups_train.nunique()
    n_sectors_test = groups.iloc[test_idx].nunique()
    overlap = set(groups_train.unique()) & set(groups.iloc[test_idx].unique())

    print(f">> Train: {len(X_train):,} rows, {n_sectors_train} sectors")
    print(f">> Test:  {len(X_test):,} rows, {n_sectors_test} sectors")
    print(f">> Sector overlap: {len(overlap)} (should be 0)")

    # ══════════════════════════════════════════════════════════════════
    # Single MLflow run wraps all 4 phases
    # ══════════════════════════════════════════════════════════════════
    with mlflow.start_run(run_name="xgb-optuna-v1") as run:
        print(f"\n>> MLflow run ID: {run.info.run_id}")

        # ── PHASE 1: Baselines ────────────────────────────────────────
        print("\n" + "=" * 72)
        print("PHASE 1 -- BASELINE COMPARISON  (grouped hold-out)")
        print("=" * 72)

        baseline_results = run_baselines(X_train, y_train, X_test, y_test)
        print()
        print_comparison(baseline_results)

        # ── PHASE 2: Optuna XGBoost ───────────────────────────────────
        print("\n" + "=" * 72)
        print("PHASE 2 -- OPTUNA XGBOOST TUNING  (GroupKFold + pruning, 50 trials)")
        print("=" * 72)

        best_params = run_optuna(X_train, y_train, groups_train, n_trials=1)

        # ── PHASE 3: Repeated grouped evaluation ──────────────────────
        print("\n" + "=" * 72)
        print(f"PHASE 3 -- REPEATED GROUPED EVALUATION  ({N_REPEATS} repeats)")
        print("=" * 72)

        tuned_model = XGBRegressor(**best_params, random_state=SEED, verbosity=0)
        pipeline_template = build_feature_pipeline(tuned_model)

        all_metrics, summary = repeated_grouped_eval(
            pipeline_template,
            X,
            y,
            groups,
            n_repeats=N_REPEATS,
        )

        print(f"\n  Mean +/- Std across {N_REPEATS} repeats:")
        for key in METRIC_KEYS:
            print(f"    {key:<20}  {summary['mean'][key]:>10.4f} +/- {summary['std'][key]:.4f}")

        # ── Fit final pipeline on primary split ───────────────────────
        print("\n>> Fitting final pipeline on primary train split...")
        pipeline = clone(pipeline_template)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        single_split_metrics = evaluate(y_test, y_pred)
        baseline_results["XGBoost (tuned)"] = single_split_metrics

        print("\n  FULL COMPARISON (baselines + tuned, primary split)")
        print()
        print_comparison(baseline_results)

        # ── Feature verification ──────────────────────────────────────
        preprocessor = pipeline.named_steps["preprocessor"]
        feature_names = list(preprocessor.get_feature_names_out())
        print(f"\n>> Total features after preprocessing: {len(feature_names)}")

        for col in ["city", "sector"]:
            matches = [f for f in feature_names if col in f.lower()]
            if matches:
                print(f"   WARNING: '{col}' found in features: {matches}")
            else:
                print(f"   OK: '{col}' not in features")

        # ── PHASE 4: Feature importance ───────────────────────────────
        print("\n" + "=" * 72)
        print("PHASE 4 -- FEATURE IMPORTANCE")
        print("=" * 72)

        export_feature_importance(pipeline, X_test, y_test, feature_names)

        # ── Log params ───────────────────────────────────────────────
        mlflow.log_params(
            {
                "seed": SEED,
                "group_col": GROUP_COL,
                "n_repeats": N_REPEATS,
                "train_rows": len(X_train),
                "test_rows": len(X_test),
                "n_sectors_train": n_sectors_train,
                **{f"optuna_{k}": v for k, v in best_params.items()},
            }
        )

        # ── Log metrics ───────────────────────────────────────────────
        # Baseline results (one metric per model per stat)
        for model_name, metrics in baseline_results.items():
            prefix = model_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
            for metric_name, val in metrics.items():
                safe_key = (
                    metric_name.replace(" ", "_")
                    .replace("/", "_")
                    .replace("(", "")
                    .replace(")", "")
                )
                mlflow.log_metric(f"{prefix}_{safe_key}", val)

        # Repeated eval summary (mean + std)
        for stat in ["mean", "std"]:
            for metric_name, val in summary[stat].items():
                safe_key = (
                    metric_name.replace(" ", "_")
                    .replace("/", "_")
                    .replace("(", "")
                    .replace(")", "")
                )
                mlflow.log_metric(f"repeated_eval_{stat}_{safe_key}", val)

        # ── Log + register pipeline ───────────────────────────────────
        print("\n" + "=" * 72)
        print("SAVING ARTIFACTS + MLFLOW LOGGING")
        print("=" * 72)

        # Also save local joblib copy (fast inference fallback)
        pipeline_path = MODEL_DIR / "pipeline_v1.joblib"
        dump(pipeline, pipeline_path)
        print(f">> Local joblib saved to: {pipeline_path}")

        # Log to MLflow registry -- input_example drives signature inference
        model_info = mlflow.sklearn.log_model(
            sk_model=pipeline,
            artifact_path="pipeline",
            registered_model_name=MLFLOW_MODEL_NAME,
            input_example=X_test.head(5),
        )
        print(f">> Model logged to MLflow: {model_info.model_uri}")

        # Transition to Staging via version returned by log_model (deterministic)
        registered_version = model_info.registered_model_version
        if registered_version:
            client = mlflow.tracking.MlflowClient()
            client.transition_model_version_stage(
                name=MLFLOW_MODEL_NAME,
                version=registered_version,
                stage="Staging",
            )
            print(f">> {MLFLOW_MODEL_NAME} v{registered_version} -> Staging")

        # Save experiment JSON (human-readable side-car)
        experiment = {
            "seed": SEED,
            "group_column": GROUP_COL,
            "n_repeats": N_REPEATS,
            "mlflow_run_id": run.info.run_id,
            "mlflow_model_version": registered_version,
            "baseline_results": baseline_results,
            "optuna_best_params": best_params,
            "repeated_eval": summary,
        }
        save_json(experiment, MODEL_DIR / "experiment_results.json")
        mlflow.log_artifact(str(MODEL_DIR / "experiment_results.json"))
        print(">> Experiment results saved + logged to MLflow")
        print("=" * 72)


if __name__ == "__main__":
    main()
