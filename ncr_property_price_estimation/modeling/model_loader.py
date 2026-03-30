"""
Model Loader — Unified model loading with MLflow Registry → Joblib fallback.

Supports both 'sales' and 'rentals' modes.
"""

from typing import Any

from ncr_property_price_estimation.config import (
    MLFLOW_MODEL_NAME,
    MLFLOW_TRACKING_URI,
    MODELS_DIR,
)


def load_model(mode: str) -> tuple[Any | None, dict[str, Any] | None]:
    """
    Load a model for the given mode ('sales' or 'rentals').

    Strategy:
        1. Try MLflow Registry (Staging stage)
        2. Fallback to local joblib

    Returns:
        (model, metadata_dict) or (None, None) if loading fails.
    """
    model, meta = _try_mlflow_load(mode)
    if model is not None:
        return model, meta

    return _try_joblib_load(mode)


def _try_mlflow_load(mode: str) -> tuple[Any | None, dict[str, Any] | None]:
    """Attempt to load a model from MLflow registry (Staging stage)."""
    try:
        import mlflow
        import mlflow.sklearn

        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

        model_name = f"{MLFLOW_MODEL_NAME}_{mode}"
        model_uri = f"models:/{model_name}/Staging"
        model = mlflow.sklearn.load_model(model_uri)

        client = mlflow.tracking.MlflowClient()
        version = None
        try:
            versions = client.get_latest_versions(model_name, stages=["Staging"])
            if versions:
                version = versions[0].version
        except Exception:
            pass

        return model, {"version": version, "source": f"mlflow_registry_{mode}"}
    except Exception as exc:
        print(f"[model-load] MLflow failed for {mode}: {exc}")
        return None, None


def _try_joblib_load(mode: str) -> tuple[Any | None, dict[str, Any] | None]:
    """Fallback to local joblib file."""
    path = MODELS_DIR / mode / f"pipeline_{mode}.joblib"
    if not path.exists():
        return None, None
    try:
        import joblib

        model = joblib.load(path)
        return model, {"version": "local", "source": str(path)}
    except Exception as e:
        print(f"[joblib] Failed to load {mode}: {e}")
        return None, None
