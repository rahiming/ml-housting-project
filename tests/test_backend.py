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


@patch("backend.app.get_model")
def test_predict_endpoint(mock_get_model):
    """Vérifie que l'endpoint predict traite correctement les données."""
    # On définit une fausse réponse du modèle
    mock_model = MagicMock()
    mock_model.predict.return_value = [2.5]
    mock_get_model.return_value = mock_model

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

    # Vérifie que le backend convertit correctement le JSON brut en DataFrame Pandas.
    # Cette étape permet au Pipeline de retrouver ses colonnes pour le preprocessing.
    mock_model.predict.assert_called_once()
    called_args, _ = mock_model.predict.call_args
    input_data = called_args[0]

    assert isinstance(
        input_data, pd.DataFrame
    ), "Le backend doit envoyer un DataFrame au pipeline"
    assert list(input_data.columns) == list(
        payload.keys()
    ), "Les colonnes doivent correspondre aux features brutes"
