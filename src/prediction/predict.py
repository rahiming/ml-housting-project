import logging

import pandas as pd

from src.prediction.model_loader import get_model

# Le schema public de l'API utilise des noms explicites. Le modele sklearn,
# lui, a ete entraine avec les noms natifs du dataset California Housing.
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

logger = logging.getLogger("uvicorn.error")


def normalize_prediction_features(data_dict: dict) -> dict:
    """Convertit le schema API vers le schema attendu par le pipeline."""
    normalized_payload = {
        FEATURE_NAME_MAP.get(feature_name, feature_name): value
        for feature_name, value in data_dict.items()
    }
    logger.info(
        "Normalisation des features terminee. champs_entree=%s champs_modele=%s",
        sorted(data_dict.keys()),
        sorted(normalized_payload.keys()),
    )
    return normalized_payload


def make_prediction(data_dict: dict) -> float:
    """Construit le DataFrame d'inference puis appelle le pipeline en memoire."""
    logger.info("Debut du calcul de prediction.")
    normalized_data = normalize_prediction_features(data_dict)
    df = pd.DataFrame([normalized_data])
    logger.info("DataFrame d'inference construit avec %s ligne(s).", len(df))
    prediction = get_model().predict(df)[0]
    logger.info("Prediction brute produite par le modele : %s", prediction)
    return float(prediction)
