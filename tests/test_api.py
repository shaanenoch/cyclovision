import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "CycloneAI" in data["title"]
    assert "disclaimer" in data

def test_cyclones_list():
    response = client.get("/api/cyclones")
    assert response.status_code == 200
    cyclones = response.json()
    assert isinstance(cyclones, list)
    assert len(cyclones) > 0
    assert cyclones[0]["name"] == "Demo Cyclone 01"

def test_search_endpoint():
    # Test place search
    response = client.get("/api/search?q=Odisha")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any("Odisha" in r["title"] for r in results)

    # Test coordinate search
    response_coord = client.get("/api/search?q=15.2, 84.7")
    assert response_coord.status_code == 200
    coord_results = response_coord.json()
    assert len(coord_results) > 0
    assert "15.2" in coord_results[0]["title"]

def test_predict_track():
    payload = {
        "current_lat": 15.2,
        "current_lon": 84.7,
        "wind_speed_kmph": 110.0,
        "pressure_hpa": 980.0,
        "movement_bearing_deg": 315.0,
        "movement_speed_kmph": 18.0
    }
    response = client.post("/api/predict-track", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert len(data["forecast"]) == 5 # +6, +12, +24, +36, +48 hr
    assert data["forecast"][0]["forecast_hour"] == 6
    assert data["forecast"][-1]["forecast_hour"] == 48
    assert "IBTrACS" in data["model_name"]
    assert data["forecast"][0]["model_mode"] == "trained"
    assert data["forecast"][0]["uncertainty_km"] > 0

def test_model_metrics():
    response = client.get("/api/model/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["model_trained"] is True
    assert "validation_accuracy" in metrics
    assert "confusion_matrix" in metrics
    assert "track_prediction_metrics" in metrics
    assert metrics["track_prediction_metrics"]["test_storms"] > 0
    assert metrics["track_prediction_metrics"]["horizons"]["48"]["mean_error_km"] > 0
    assert metrics["classification_model_trained"] is False
