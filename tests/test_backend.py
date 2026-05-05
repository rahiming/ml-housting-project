from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

# On mock le chargement du modèle avant d'importer l'app
# pour permettre aux tests de tourner même sans artefacts réels.
with patch("backend.app.get_latest_model", return_value=MagicMock()):
    from backend.app import app

client = TestClient(app)


def test_health_endpoint():
    """Vérifie que l'API est en ligne."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("backend.app.model")
def test_predict_endpoint(mock_model):
    """Vérifie que l'endpoint predict traite correctement les données."""
    # On définit une fausse réponse du modèle
    mock_model.predict.return_value = [2.5]

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
