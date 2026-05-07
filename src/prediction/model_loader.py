import logging

import joblib

from src.prediction import config

logger = logging.getLogger("uvicorn.error")

_model = None


def get_latest_model():
    """Charge le meilleur modele disponible pour l'inference."""
    logger.info("Recherche du modele a charger.")
    latest_prod_model = config.MODELS_PATH / config.MODEL_LATEST_NAME

    if latest_prod_model.exists():
        logger.info("Chargement prioritaire du modele latest : %s", latest_prod_model)
        return joblib.load(latest_prod_model)

    logger.info(
        "Modele latest absent. Recherche des modeles versionnes via %s.",
        config.MODEL_VERSION_PATTERN,
    )
    models = list(config.MODELS_PATH.glob(config.MODEL_VERSION_PATTERN))

    if not models:
        logger.error("Aucun modele trouve dans %s", config.MODELS_PATH)
        raise FileNotFoundError("Aucun modele trouve dans le dossier artifacts.")

    latest_model_path = sorted(models, key=lambda x: int(x.stem.split("_v")[-1]))[-1]
    logger.info("Chargement du modele versionne le plus recent : %s", latest_model_path)
    return joblib.load(latest_model_path)


def get_model():
    """Retourne un singleton du modele charge en memoire."""
    global _model

    if _model is None:
        logger.info("Aucun modele en cache. Chargement depuis le disque.")
        _model = get_latest_model()
    else:
        logger.info("Modele deja en cache. Reutilisation de l'instance memoire.")

    return _model
