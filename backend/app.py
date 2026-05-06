from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.prediction.predict import make_prediction
from src.prediction.model_loader import get_model
from src.prediction.schemas import HousingFeatures

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pré-chargement du modèle au démarrage pour éviter les timeouts
    try:
        get_model()
    except Exception:
        pass  # Évite de bloquer si le modèle est absent (ex: en CI)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: HousingFeatures):
    # Appel du service de prédiction découplé
    prediction = make_prediction(data.model_dump())
    return {"prediction": prediction}
