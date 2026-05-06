from pathlib import Path
from unittest.mock import MagicMock, patch

from src.prediction.model_loader import get_latest_model


@patch("src.prediction.model_loader.Path.exists")
@patch("src.prediction.model_loader.Path.glob")
def test_get_latest_model_versions(mock_glob, mock_exists):
    """Vérifie que le chargeur prend bien la version la plus élevée."""
    mock_exists.return_value = False  # On force le scan des versions

    mock_v1 = MagicMock(spec=Path)
    mock_v1.stem = "model_v1"
    mock_v2 = MagicMock(spec=Path)
    mock_v2.stem = "model_v2"

    mock_glob.return_value = [mock_v1, mock_v2]

    with patch("src.prediction.model_loader.joblib.load") as mock_load:
        get_latest_model()
        # On vérifie que joblib.load a été appelé avec mock_v2 (le plus récent)
        # sorted par le chiffre après '_v'
        args, _ = mock_load.call_args
        called_path = args[0]
        assert called_path.stem == "model_v2"


@patch("src.prediction.model_loader.Path.exists")
def test_get_latest_model_priority(mock_exists):
    """Vérifie que model_latest.joblib est prioritaire."""
    mock_exists.return_value = True

    with patch("src.prediction.model_loader.joblib.load") as mock_load:
        get_latest_model()

        # Vérifie que joblib.load a été appelé avec model_latest
        args, _ = mock_load.call_args
        called_path = args[0]
        assert called_path.stem == "model_latest"
