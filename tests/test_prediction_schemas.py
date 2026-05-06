import pytest
from pydantic import ValidationError
from src.prediction.schemas import HousingFeatures


def test_housing_features_valid_data():
    """Vérifie la validation des données d'entrée."""
    data = {
        "MedInc": 3.0,
        "HouseAge": 15.0,
        "AveRooms": 5.0,
        "AveBedrms": 1.0,
        "Population": 800.0,
        "AveOccup": 3.0,
        "Latitude": 37.0,
        "Longitude": -122.0,
    }
    features = HousingFeatures(**data)
    assert features.MedInc == 3.0


def test_housing_features_invalid_data():
    """Vérifie que Pydantic rejette les types incorrects."""
    data = {"MedInc": "not-a-number", "HouseAge": 15.0}
    with pytest.raises(ValidationError):
        HousingFeatures(**data)
