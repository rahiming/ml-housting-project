from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class HousingFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


def get_latest_model():
    """Trouve et charge le modèle avec le numéro de version le plus élevé."""
    artifacts_path = Path("artifacts")
    models = list(artifacts_path.glob("model_v*.joblib"))
    if not models:
        # Fallback au modèle sans version si existant
        default_model = artifacts_path / "model.joblib"
        if default_model.exists():
            return joblib.load(default_model)  # nosec B301
        raise FileNotFoundError("Aucun modèle trouvé dans le dossier artifacts.")

    # Trie par numéro de version et prend le dernier
    latest_model_path = sorted(models, key=lambda x: int(x.stem.split("_v")[-1]))[-1]
    return joblib.load(latest_model_path)  # nosec B301


_model = None


def get_model():
    """Charge le modèle au premier appel (Lazy Loading)."""
    global _model
    if _model is None:
        _model = get_latest_model()
    return _model


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: HousingFeatures):
    """
    Endpoint de prédiction qui reçoit les données brutes, les prétraite
    via le pipeline et retourne l'estimation.
    """  # Conversion des données Pydantic en DataFrame Pandas.
    # Le pipeline a été entraîné avec des noms de colonnes (via set_output="pandas"),
    # il est donc important de passer un DataFrame pour que les transformations
    # (comme l'ingénierie de variables dans features.py) s'appliquent correctement.
    df = pd.DataFrame([data.model_dump()])

    # Le pipeline (imputer -> engineer -> scaler -> regressor) s'exécute intégralement.
    prediction = get_model().predict(df)[0]
    return {"prediction": float(prediction)}
