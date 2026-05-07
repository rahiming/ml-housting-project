import joblib

from src.prediction import config


def get_latest_model():
    """Trouve et charge le modèle avec le numéro de version le plus élevé."""
    # Priorité absolue au modèle de production "latest"
    latest_prod_model = config.MODELS_PATH / config.MODEL_LATEST_NAME

    if latest_prod_model.exists():
        return joblib.load(latest_prod_model)

    models = list(config.MODELS_PATH.glob(config.MODEL_VERSION_PATTERN))

    if not models:
        raise FileNotFoundError("Aucun modèle trouvé dans le dossier artifacts.")

    latest_model_path = sorted(models, key=lambda x: int(x.stem.split("_v")[-1]))[-1]
    return joblib.load(latest_model_path)


_model = None


def get_model():
    global _model
    if _model is None:
        _model = get_latest_model()
    return _model
