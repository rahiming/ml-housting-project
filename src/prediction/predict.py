import pandas as pd

from src.prediction.model_loader import get_model

FEATURE_NAME_MAP = {
    "median_income": "MedInc",
    "housing_median_age": "HouseAge",
    "average_rooms": "AveRooms",
    "average_bedrooms": "AveBedrms",
    "population": "Population",
    "average_occupancy": "AveOccup",
    "latitude": "Latitude",
    "longitude": "Longitude",
}


def normalize_prediction_features(data_dict: dict) -> dict:
    """Convertit les noms d'entree de l'API vers ceux attendus par le modele."""
    return {
        FEATURE_NAME_MAP.get(feature_name, feature_name): value
        for feature_name, value in data_dict.items()
    }


def make_prediction(data_dict: dict) -> float:
    normalized_data = normalize_prediction_features(data_dict)
    df = pd.DataFrame([normalized_data])
    prediction = get_model().predict(df)[0]
    return float(prediction)
