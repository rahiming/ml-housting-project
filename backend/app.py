import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.storage.s3_client import download_model_from_s3
from src.prediction.model_loader import get_model
from src.prediction.predict import make_prediction
from src.prediction.schemas import HousingFeatures

# Utiliser le logger d'uvicorn pour garantir la visibilite dans les logs Docker
logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("SKIP_MINIO_STARTUP", "0") == "1":
        logger.info(
            "Initialisation MinIO et chargement du modele ignores pour les tests."
        )
        yield
        return

    # 1. Telechargement du modele depuis MinIO
    try:
        model_path = download_model_from_s3()
        logger.info(f"Modele telecharge et pret a etre charge depuis : {model_path}")
    except Exception as e:
        logger.error(f"Erreur critique lors du telechargement du modele : {e}")
        raise RuntimeError(
            f"L'application ne peut pas demarrer sans modele : {e}"
        ) from e

    # 2. Pre-chargement du modele en memoire via le model_loader
    try:
        # get_model() va maintenant trouver le modele telecharge et le charger
        get_model()
        logger.info("Modele pre-charge en memoire au demarrage.")
    except Exception as e:
        logger.error(f"Erreur critique lors du pre-chargement du modele : {e}")
        raise RuntimeError(
            f"L'application ne peut pas demarrer sans modele : {e}"
        ) from e

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def index():
    return {"message": "ML Housing Prediction API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: HousingFeatures):
    # Appel du service de prediction decouple
    prediction = make_prediction(data.model_dump())
    return {"prediction": prediction}
