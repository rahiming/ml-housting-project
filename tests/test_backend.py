from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_health_endpoint():
    """Vérifie que l'API est en ligne."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("backend.app.get_models", side_effect=FileNotFoundError("A/B models missing"))
@patch("backend.app.make_prediction")
def test_predict_endpoint(mock_predict, mock_get_models):
    """Vérifie que l'endpoint predict traite correctement les données."""
    # On définit une fausse réponse du service de prédiction
    mock_predict.return_value = 2.5

    payload = {
        "median_income": 3.5,
        "housing_median_age": 20.0,
        "average_rooms": 5.0,
        "average_bedrooms": 1.0,
        "population": 1000.0,
        "average_occupancy": 3.0,
        "latitude": 34.0,
        "longitude": -118.0,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["prediction"] == 2.5
    assert response_data["variant"] == "A"
    assert response_data["model_version"] == "legacy_single_model"
    assert response_data["execution_mode"] == "legacy_fallback"
    assert isinstance(response_data["latency_ms"], float)
    assert response_data["request_id"]
    # Vérifie que le service a été appelé avec les bonnes données
    mock_predict.assert_called_once_with(payload)
    mock_get_models.assert_called_once()


@patch("backend.app.log_prediction")
@patch("backend.app.get_models")
def test_predict_endpoint_with_ab_registry(mock_get_models, mock_log_prediction):
    """Vérifie que l'endpoint utilise le registry A/B quand il est disponible."""
    mock_pipeline = mock_get_models.return_value["B"]
    mock_pipeline.predict.return_value = [3.14]

    payload = {
        "user_id": "alice",
        "median_income": 3.5,
        "housing_median_age": 20.0,
        "average_rooms": 5.0,
        "average_bedrooms": 1.0,
        "population": 1000.0,
        "average_occupancy": 3.0,
        "latitude": 34.0,
        "longitude": -118.0,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["prediction"] == 3.14
    assert response_data["variant"] == "B"
    assert response_data["model_version"] == "model_v2"
    assert response_data["execution_mode"] == "ab_registry"
    assert isinstance(response_data["latency_ms"], float)
    assert response_data["request_id"]
    mock_pipeline.predict.assert_called_once()
    mock_log_prediction.assert_called_once()
