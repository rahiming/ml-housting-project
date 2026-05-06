from pathlib import Path

import joblib


def get_latest_model():
    """Trouve et charge le modèle avec le numéro de version le plus élevé."""
    artifacts_path = Path("artifacts/models")

    # Priorité absolue au modèle de production "latest"
    latest_prod_model = artifacts_path / "model_latest.joblib"
    if latest_prod_model.exists():
        return joblib.load(latest_prod_model)

    models = list(artifacts_path.glob("model_v*.joblib"))

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
