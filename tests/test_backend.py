from unittest.mock import MagicMock, patch

import pandas as pd
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
        "MedInc": 3.5,
        "HouseAge": 20.0,
        "AveRooms": 5.0,
        "AveBedrms": 1.0,
        "Population": 1000.0,
        "AveOccup": 3.0,
        "Latitude": 34.0,
        "Longitude": -118.0,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json() == {"prediction": 2.5}
    # Vérifie que le service a été appelé avec les bonnes données
    mock_predict.assert_called_once_with(payload)
