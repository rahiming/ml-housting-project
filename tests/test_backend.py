from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_health_endpoint():
    """Vérifie que l'API est en ligne."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("backend.app.make_prediction")
def test_predict_endpoint(mock_predict):
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
    assert response.json() == {"prediction": 2.5}
    # Vérifie que le service a été appelé avec les bonnes données
    mock_predict.assert_called_once_with(payload)
