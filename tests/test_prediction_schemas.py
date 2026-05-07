import pytest
from pydantic import ValidationError

from src.prediction.schemas import HousingFeatures


def test_housing_features_valid_data():
    """Vérifie la validation des données d'entrée."""
    data = {
        "median_income": 3.0,
        "housing_median_age": 15.0,
        "average_rooms": 5.0,
        "average_bedrooms": 1.0,
        "population": 800.0,
        "average_occupancy": 3.0,
        "latitude": 37.0,
        "longitude": -122.0,
    }
    features = HousingFeatures(**data)
    assert features.median_income == 3.0


def test_housing_features_invalid_data():
    """Vérifie que Pydantic rejette les types incorrects."""
    data = {"MedInc": "not-a-number", "HouseAge": 15.0}
    with pytest.raises(ValidationError):
        HousingFeatures(**data)
