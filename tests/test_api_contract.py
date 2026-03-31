"""
API Contract Tests.

Verifies that the FastAPI endpoints follow the documented Pydantic schemas.
Uses unittest.mock to bypass real model inference, focusing on the interface.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from ncr_property_price_estimation.api import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# 1. Health & Meta Endpoints
# ---------------------------------------------------------------------------


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint():
    # Mock global _models and _discovery_pool state for a predictable response
    with patch(
        "ncr_property_price_estimation.api._models", {"sales": MagicMock(), "rentals": MagicMock()}
    ), patch(
        "ncr_property_price_estimation.api._discovery_pool"
    ) as mock_pool:
        mock_pool.empty = False
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["sales_loaded"] is True
        assert data["rentals_loaded"] is True


# ---------------------------------------------------------------------------
# 2. Prediction Contract (Pydantic Validation)
# ---------------------------------------------------------------------------


@patch("ncr_property_price_estimation.api._predict_internal")
def test_predict_single_contract(mock_predict):
    """Verify that a valid payload returns the expected PredictionResponse schema."""
    # Mock a valid response dictionary
    mock_resp = {
        "price_per_sqft": 8500.0,
        "estimated_market_value": 10200000.0,
        "predicted_monthly_rent": 25000.0,
        "property_name": "Emaar Palm Drive",
        "intelligence_suite": {"unified_score": 8.5},
        "recommendations": [],
        "similar_listings": [],
    }
    mock_predict.return_value = [mock_resp]

    # Valid payload matching PropertyInput
    payload = {
        "area": 1200.0,
        "bedrooms": 3,
        "bathrooms": 2,
        "prop_type": "Apartment",
        "furnishing_status": "Semi-Furnished",
        "legal_status": "Freehold",
        "city": "Gurugram",
        "sector": "Sector 50",
        "property_name": "Emaar Palm Drive",
        "is_luxury": False,
    }

    # We must patch _models check in predict()
    with patch("ncr_property_price_estimation.api._models", {"sales": True}):
        response = client.post("/predict", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "price_per_sqft" in data
    assert "intelligence_suite" in data


def test_predict_invalid_payload_triggers_422():
    """Verify that Pydantic properly blocks invalid data (e.g. area <= 0)."""
    payload = {
        "area": -1.0,  # INVALID: must be > 0
        "bedrooms": 0,  # INVALID: must be >= 1
        "prop_type": "Castle",  # INVALID: not in Literal
        "city": "Gurgaon",
        "sector": "Sector 50",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Unprocessable Entity


# ---------------------------------------------------------------------------
# 3. Batch Prediction Contract
# ---------------------------------------------------------------------------


@patch("ncr_property_price_estimation.api._predict_internal")
def test_predict_batch_contract(mock_predict):
    """Verify batch prediction contract with 100% schema parity."""
    mock_resp = {
        "price_per_sqft": 8500.0,
        "estimated_market_value": 10200000.0,
        "predicted_monthly_rent": 25000.0,
        "property_name": "Mock",
        "intelligence_suite": {"unified_score": 8.5},
        "recommendations": [],
        "similar_listings": [],
    }
    mock_predict.return_value = [mock_resp, mock_resp]

    payload = [
        {"area": 1000, "bedrooms": 2, "prop_type": "Apartment", "city": "Noida", "sector": "1"},
        {
            "area": 2000,
            "bedrooms": 4,
            "prop_type": "Independent House",
            "city": "Gurgaon",
            "sector": "2",
        },
    ]

    with patch("ncr_property_price_estimation.api._models", {"sales": True}):
        response = client.post("/predict/batch", json=payload)

    assert response.status_code == 200
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# 4. Discovery & Hotspots Contract
# ---------------------------------------------------------------------------


def test_get_hotspots_invalid_params():
    """Verify Literal constraints on query parameters."""
    response = client.get("/intelligence/hotspots?listing_type=invalid")
    assert response.status_code == 422
