import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# On force le mode test avant d'importer l'application pour éviter
# les appels réseau/disque
# dans le cycle de vie lifespan de FastAPI (MinIO, chargement de modèles réels).
os.environ["SKIP_MINIO_STARTUP"] = "1"

from backend.app import app

client = TestClient(app)


@pytest.fixture
def valid_payload():
    """Retourne un payload valide pour l'endpoint /predict."""
    return {
        "median_income": 3.5,
        "housing_median_age": 20.0,
        "average_rooms": 5.0,
        "average_bedrooms": 1.0,
        "population": 1000.0,
        "average_occupancy": 3.0,
        "latitude": 34.0,
        "longitude": -118.0,
        "user_id": "test_user",
    }


def test_health_endpoint():
    """Vérifie que le point de terminaison de santé fonctionne."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_fallback_mode(valid_payload):
    """
    Simule l'absence des modèles A/B et vérifie que l'API bascule
    correctement sur le modèle legacy avec un code HTTP 200.
    """
    # On patche 'get_models' pour lever une exception FileNotFoundError
    # On patche 'make_prediction' pour retourner une valeur fixe prévisible
    with (
        patch("backend.app.get_models") as mock_get_models,
        patch("backend.app.make_prediction") as mock_make_prediction,
    ):
        mock_get_models.side_effect = FileNotFoundError(
            "Models registry not initialized"
        )
        mock_make_prediction.return_value = 1.99

        response = client.post("/predict", json=valid_payload)

        assert response.status_code == 200
        data = response.json()

        # Vérifications de la logique de fallback
        assert data["prediction"] == 1.99
        assert data["execution_mode"] == "legacy_fallback"
        assert data["model_version"] == "legacy_single_model"
        assert "request_id" in data


def test_predict_ab_registry_mode(valid_payload):
    """
    Vérifie que l'API utilise le registre A/B quand les modèles sont disponibles.
    """
    with patch("backend.app.get_models") as mock_get_models:
        # On crée un mock de modèle sklearn avec une méthode predict
        mock_model = MagicMock()
        mock_model.predict.return_value = [2.5]

        # Le registry retourne un dictionnaire de modèles pour les variantes A et B
        mock_get_models.return_value = {"A": mock_model, "B": mock_model}

        response = client.post("/predict", json=valid_payload)

        assert response.status_code == 200
        data = response.json()

        assert data["prediction"] == 2.5
        assert data["execution_mode"] == "ab_registry"
        assert data["variant"] in ["A", "B"]
