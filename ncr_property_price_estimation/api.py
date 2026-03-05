"""
FastAPI prediction service for NCR property price estimation.

Loads the trained sklearn pipeline from MLflow registry (Production stage)
or falls back to a local joblib artifact on startup.

Endpoints:
    GET  /             — API welcome
    GET  /health       — Liveness + model status
    POST /predict      — Single property prediction
    POST /predict/batch — Batch predictions (max 50)
    GET  /model-info   — Model registry metadata
"""

import os
from contextlib import asynccontextmanager
from typing import Literal

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Ensure package imports work when running via uvicorn
# ---------------------------------------------------------------------------
from ncr_property_price_estimation.config import (
    API_HOST,
    API_PORT,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_MODEL_NAME,
    MLFLOW_TRACKING_URI,
    MODELS_DIR,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BATCH_LIMIT = 50

# Exact column order the pipeline expects at .predict() time.
# Must match features.py FeatureCreator + GeoMedianEncoder input.
PIPELINE_INPUT_COLUMNS = [
    "area",
    "bedrooms",
    "bathrooms",
    "balcony",
    "floor",
    "prop_type",
    "furnished",
    "facing",
    "city",
    "sector",
    "pooja_room",
    "servant_room",
    "store_room",
    "pool",
    "gym",
    "lift",
    "parking",
    "vastu_compliant",
]


# ---------------------------------------------------------------------------
# Pydantic schemas — strict Literal constraints for categoricals
# ---------------------------------------------------------------------------
class PropertyInput(BaseModel):
    """Input schema for a single property prediction."""

    area: float = Field(..., gt=0, description="Built-up area in sqft")
    bedrooms: int = Field(..., ge=1, description="Number of bedrooms")
    bathrooms: int | None = Field(None, ge=0, description="Number of bathrooms")
    balcony: int = Field(0, ge=0, description="Number of balconies")
    floor: int | None = Field(None, ge=0, description="Floor number")

    prop_type: Literal["Apartment", "Builder Floor", "Independent House"] = Field(
        ..., description="Property type"
    )
    furnished: Literal["Fully-Furnished", "Semi-Furnished", "Unfurnished", "Unknown"] = Field(
        "Unknown", description="Furnishing status"
    )
    facing: Literal[
        "East",
        "North",
        "North-East",
        "North-West",
        "South",
        "South-East",
        "South-West",
        "West",
        "Unknown",
    ] = Field("Unknown", description="Property facing direction")

    city: Literal["Delhi", "Faridabad", "Ghaziabad", "Greater Noida", "Gurugram", "Noida"] = Field(
        ..., description="City in NCR"
    )
    sector: str = Field(..., min_length=1, description="Sector / locality name")

    # Amenity flags (0 = absent, 1 = present)
    pooja_room: int = Field(0, ge=0, le=1)
    servant_room: int = Field(0, ge=0, le=1)
    store_room: int = Field(0, ge=0, le=1)
    pool: int = Field(0, ge=0, le=1)
    gym: int = Field(0, ge=0, le=1)
    lift: int = Field(0, ge=0, le=1)
    parking: int = Field(0, ge=0, le=1)
    vastu_compliant: int = Field(0, ge=0, le=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "area": 1200,
                    "bedrooms": 3,
                    "prop_type": "Apartment",
                    "city": "Gurugram",
                    "sector": "Sector 50",
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Output schema for a single prediction."""

    price_per_sqft: float = Field(..., description="Predicted price in ₹/sqft")
    estimated_total_price: float = Field(
        ..., description="Estimated total price (price_per_sqft × area)"
    )


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_stage: str | None = None


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str | None = None
    run_id: str | None = None
    experiment_name: str


# ---------------------------------------------------------------------------
# Global state — populated during lifespan
# ---------------------------------------------------------------------------
_model = None
_model_meta = {
    "loaded": False,
    "stage": None,
    "version": None,
    "run_id": None,
    "source": None,
}


# ---------------------------------------------------------------------------
# Model loading helpers
# ---------------------------------------------------------------------------
def _try_mlflow_load():
    """Attempt to load model from MLflow registry (Production stage).

    Uses mlflow.sklearn.load_model (not pyfunc) to get the raw sklearn
    pipeline — avoids pyfunc's strict schema enforcement which rejects
    int64→int32 and int64→float64 coercion.
    """
    try:
        import mlflow
        import mlflow.sklearn

        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

        model_uri = f"models:/{MLFLOW_MODEL_NAME}/Production"
        model = mlflow.sklearn.load_model(model_uri)

        # Extract metadata from registry
        client = mlflow.tracking.MlflowClient()
        version = None
        run_id = None
        try:
            versions = client.get_latest_versions(MLFLOW_MODEL_NAME, stages=["Production"])
            if versions:
                version = versions[0].version
                run_id = versions[0].run_id
        except Exception:
            pass

        return model, {
            "loaded": True,
            "stage": "Production",
            "version": str(version) if version else None,
            "run_id": run_id,
            "source": "mlflow_registry",
        }
    except Exception as exc:
        print(f"[model-load] MLflow registry failed: {exc}")
        return None, None


def _try_joblib_load():
    """Attempt to load model from local joblib file."""
    joblib_path = MODELS_DIR / "pipeline_v1.joblib"
    if not joblib_path.exists():
        return None, None
    try:
        import joblib

        model = joblib.load(joblib_path)
        return model, {
            "loaded": True,
            "stage": "local_fallback",
            "version": None,
            "run_id": None,
            "source": str(joblib_path),
        }
    except Exception as exc:
        print(f"[model-load] Joblib load failed: {exc}")
        return None, None


# ---------------------------------------------------------------------------
# Lifespan — load model before accepting requests
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _model_meta

    # 1. Try MLflow Production
    model, meta = _try_mlflow_load()

    # 2. Fallback to local joblib
    if model is None:
        print("[model-load] Falling back to local joblib...")
        model, meta = _try_joblib_load()

    # 3. Both failed → refuse to start
    if model is None:
        raise RuntimeError(
            "Could not load model from MLflow registry or local joblib. "
            "Server cannot start without a model."
        )

    _model = model
    _model_meta = meta
    print(f"[model-load] Model loaded successfully from {meta['source']}")

    yield  # app runs

    # Cleanup (nothing to do)
    _model = None


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="NCR Property Price API",
    description="Predict property prices per sqft in the National Capital Region.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — configurable via CORS_ORIGINS env var (comma-separated)
# ---------------------------------------------------------------------------
_cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Prediction helper
# ---------------------------------------------------------------------------
def _predict(inputs: list[PropertyInput]) -> list[PredictionResponse]:
    """Build DataFrame in fixed column order, predict, convert from log scale."""

    # Build rows as dicts, respecting exact column order
    rows = []
    for inp in inputs:
        rows.append({col: getattr(inp, col) for col in PIPELINE_INPUT_COLUMNS})

    df = pd.DataFrame(rows, columns=PIPELINE_INPUT_COLUMNS)

    # Pipeline predicts log(price_per_sqft) → expm1 to get ₹/sqft
    pred_log = _model.predict(df)

    pred = np.expm1(pred_log)

    results = []
    for i, inp in enumerate(inputs):
        price_sqft = float(pred[i])
        results.append(
            PredictionResponse(
                price_per_sqft=round(price_sqft, 2),
                estimated_total_price=round(price_sqft * inp.area, 2),
            )
        )

    return results


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    """API welcome message."""
    return {"message": "NCR Property Price API"}


@app.get("/health", response_model=HealthResponse)
def health():
    """Liveness check with model status."""
    return HealthResponse(
        status="healthy",
        model_loaded=_model_meta["loaded"],
        model_stage=_model_meta["stage"],
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(property_input: PropertyInput):
    """Predict price per sqft for a single property."""
    if not _model_meta["loaded"]:
        raise HTTPException(status_code=503, detail="Model not loaded")

    results = _predict([property_input])
    return results[0]


@app.post("/predict/batch", response_model=list[PredictionResponse])
def predict_batch(properties: list[PropertyInput]):
    """Predict price per sqft for multiple properties (max 50)."""
    if not _model_meta["loaded"]:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if len(properties) == 0:
        raise HTTPException(status_code=422, detail="Empty batch")

    if len(properties) > BATCH_LIMIT:
        raise HTTPException(
            status_code=413,
            detail=f"Batch size {len(properties)} exceeds limit of {BATCH_LIMIT}",
        )

    return _predict(properties)


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    """Return current model metadata."""
    return ModelInfoResponse(
        model_name=MLFLOW_MODEL_NAME,
        model_version=_model_meta["version"],
        run_id=_model_meta["run_id"],
        experiment_name=MLFLOW_EXPERIMENT_NAME,
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "ncr_property_price_estimation.api:app",
        host=API_HOST,
        port=API_PORT,
    )
