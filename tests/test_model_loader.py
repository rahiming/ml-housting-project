from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.prediction.model_loader import get_latest_model, get_model


@patch("src.prediction.model_loader.config")
def test_get_latest_model_versions(mock_config):
    """Verifie que le chargeur prend bien la version la plus elevee."""
    mock_config.MODELS_PATH.__truediv__.return_value.exists.return_value = False

    mock_v1 = MagicMock(spec=Path)
    mock_v1.stem = "model_v1"
    mock_v2 = MagicMock(spec=Path)
    mock_v2.stem = "model_v2"

    mock_config.MODELS_PATH.glob.return_value = [mock_v1, mock_v2]

    with patch("src.prediction.model_loader.joblib.load") as mock_load:
        get_latest_model()
        args, _ = mock_load.call_args
        called_path = args[0]
        assert called_path.stem == "model_v2"


@patch("src.prediction.model_loader.config")
def test_get_latest_model_not_found(mock_config):
    """Verifie qu'une erreur est levee si aucun modele n'est trouve."""
    mock_config.MODELS_PATH.__truediv__.return_value.exists.return_value = False
    mock_config.MODELS_PATH.glob.return_value = []

    with pytest.raises(
        FileNotFoundError, match="Aucun mod.*le trouv.* dans le dossier artifacts."
    ):
        get_latest_model()


@patch("src.prediction.model_loader.get_latest_model")
def test_get_model_singleton(mock_get_latest):
    """Verifie que get_model charge le modele une seule fois en memoire."""
    from src.prediction import model_loader

    model_loader._model = None
    mock_get_latest.return_value = MagicMock()

    get_model()
    get_model()
    assert mock_get_latest.call_count == 1


@patch("src.prediction.model_loader.config")
def test_get_latest_model_priority(mock_config):
    """Verifie que model_latest.joblib est prioritaire."""
    latest_model = Path("artifacts/models/model_latest.joblib")
    mock_config.MODEL_LATEST_NAME = "model_latest.joblib"
    mock_config.MODELS_PATH.__truediv__.return_value = latest_model

    with patch.object(Path, "exists", return_value=True):
        with patch("src.prediction.model_loader.joblib.load") as mock_load:
            get_latest_model()

            args, _ = mock_load.call_args
            called_path = args[0]
            assert called_path == latest_model
