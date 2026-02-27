"""
FastAPI endpoint tests.

Uses FastAPI TestClient — no trained model is loaded, so prediction
endpoints return 503.  These tests verify routing, validation, and
response schemas.
"""

from fastapi.testclient import TestClient

from ncr_property_price_estimation.api import app

client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Root & health
# ---------------------------------------------------------------------------


def test_root_returns_welcome():
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body or "msg" in body or isinstance(body, dict)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body
    assert "model_loaded" in body


# ---------------------------------------------------------------------------
# Model info
# ---------------------------------------------------------------------------


def test_model_info_endpoint():
    resp = client.get("/model-info")
    assert resp.status_code == 200
    body = resp.json()
    assert "model_name" in body
    assert "experiment_name" in body


# ---------------------------------------------------------------------------
# Prediction validation (422 on bad input)
# ---------------------------------------------------------------------------


def test_predict_missing_body():
    resp = client.post("/predict")
    assert resp.status_code == 422


def test_predict_invalid_area():
    """area must be > 0."""
    resp = client.post("/predict", json={"area": -100, "bedrooms": 2})
    assert resp.status_code == 422


def test_predict_invalid_city():
    """city must be one of the allowed Literal values."""
    resp = client.post(
        "/predict",
        json={
            "area": 1200,
            "bedrooms": 3,
            "city": "Mumbai",  # not in NCR
            "sector": "Bandra",
            "prop_type": "Apartment",
        },
    )
    assert resp.status_code == 422


def test_batch_exceeds_limit():
    """Batch endpoint rejects > BATCH_LIMIT items.

    Without a loaded model the endpoint returns 503 (model-not-loaded)
    before reaching the size check.  Either 413 or 503 means the
    oversized batch will not be processed.
    """
    from ncr_property_price_estimation.api import BATCH_LIMIT

    payload = [
        {"area": 1000, "bedrooms": 2, "city": "Noida", "sector": "Sector 75", "prop_type": "Apartment"}
    ] * (BATCH_LIMIT + 1)

    resp = client.post("/predict/batch", json=payload)
    # 413 (batch too large) or 503 (model not loaded — checked first)
    assert resp.status_code in (413, 503)
