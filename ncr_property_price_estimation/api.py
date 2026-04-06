"""
Unified Modular API Shell — Decoupled NCR Property Intelligence Suite.
Manages high-performance spatial audits, ML-driven benchmarks, and ROI discovery.
"""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from ncr_property_price_estimation import state
from ncr_property_price_estimation.config import API_HOST, API_PORT
from ncr_property_price_estimation.routes import (
    debug,
    discover,
    intelligence,
    predict,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Institutional state hydration shell."""
    await state.load_institutional_state()
    yield
    state.clear_state()

app = FastAPI(
    title="NCR Property Intelligence (Modular)",
    description="Decoupled AI-driven valuation and discovery engine for NCR Real Estate.",
    version="stable-v2.0",
    lifespan=lifespan,
)

# CORS — Clinical Synchronization
_cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.29.249:3000",
    "http://192.168.29.249:3000/",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]
_env_origins = os.environ.get("CORS_ORIGINS")
if _env_origins:
    # Ensure env origins are cleaned of any whitespace or trailing slashes
    _cors_origins.extend([o.strip().rstrip("/") for o in _env_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTER UNIFICATION ──────────────────────────────────────────
# We maintain legacy path consistency for frontend synchronization.

# 1. Valuation Engines (POST /predict, POST /predict/batch)
app.include_router(predict.router)

# 2. Discovery Engines (POST /discover, GET /discover/hotspots)
app.include_router(discover.router)

# 3. Institutional Intelligence (GET /locality/list, GET /intelligence/localities)
app.include_router(intelligence.router)

# 4. Diagnostics (GET /debug/*)
app.include_router(debug.router)

# ── TOP-LEVEL ENDPOINTS ──────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "NCR Property Intelligence (Modular Engine Active)"}

@app.get("/health")
def health(response: Response):
    """Root-level tactical health audit."""
    if state.discovery_pool.empty:
        response.status_code = 503
    return {
        "status": "healthy" if not state.discovery_pool.empty else "degraded",
        "models_loaded": list(state.models.keys()),
        "discovery_size": len(state.discovery_pool)
    }

# ── LEGACY PATH MAPPING ──────────────────────────────────────────
# Ensure /locality/list maps to the new intelligence router logic.
@app.get("/locality/list", tags=["Institutional Metadata"])
def get_legacy_locality_list(city: str):
    """Bridge for legacy frontend locality recovery."""
    return intelligence.get_locality_list(city)

@app.get("/model-info", tags=["Institutional Metadata"])
def get_legacy_model_info():
    """Bridge for legacy frontend model-info recovery."""
    return intelligence.get_model_info()

if __name__ == "__main__":
    uvicorn.run("ncr_property_price_estimation.api:app", host=API_HOST, port=API_PORT)
