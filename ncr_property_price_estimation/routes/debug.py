import os

from fastapi import APIRouter

from ncr_property_price_estimation import state
from ncr_property_price_estimation.config import PROJ_ROOT

router = APIRouter(prefix="/debug", tags=["Diagnostics & Debug"])


@router.get("/model")
def debug_model():
    """Institutional model audit."""
    return {
        k: {"type": str(type(v)), "meta": state.model_meta.get(k)} for k, v in state.models.items()
    }


@router.get("/locality")
def debug_locality():
    """Institutional locality indexing audit."""
    return {
        "cities": list(state.locality_index.keys()),
        "total_cities": len(state.locality_index),
        "sample": {c: list(v.keys())[:5] for c, v in state.locality_index.items()},
    }


@router.get("/pool")
def debug_pool():
    """Institutional discovery pool audit."""
    if state.discovery_pool.empty:
        return {"status": "empty"}
    return {
        "size": len(state.discovery_pool),
        "columns": list(state.discovery_pool.columns),
        "city_counts": state.discovery_pool["city"].value_counts().to_dict(),
    }


@router.get("/fs")
def debug_fs():
    """Tactical filesystem audit."""
    return {
        "proj_root": str(PROJ_ROOT),
        "data_contents": os.listdir(PROJ_ROOT / "data")
        if (PROJ_ROOT / "data").exists()
        else "Missing",
        "cwd": os.getcwd(),
    }
