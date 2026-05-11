from unittest.mock import MagicMock, patch

from src.prediction.predict import make_prediction


@patch("src.prediction.predict.get_model")
def test_make_prediction_logic(mock_get_model):
    """Vérifie que make_prediction appelle le modèle et retourne un float."""
    mock_model = MagicMock()
    mock_model.predict.return_value = [4.5]
    mock_get_model.return_value = mock_model

    data = {"MedInc": 3.0, "HouseAge": 15.0}
    result = make_prediction(data)

    assert isinstance(result, float)
    assert result == 4.5
    mock_model.predict.assert_called_once()
