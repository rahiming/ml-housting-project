import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.storage.s3_client import download_model_from_s3
from src.prediction.model_loader import get_model
from src.prediction.predict import make_prediction
from src.prediction.schemas import HousingFeatures

# Le backend reutilise le logger uvicorn afin de centraliser les logs applicatifs
# dans la meme sortie que les logs HTTP lorsque l'application tourne dans Docker.
logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare l'application avant l'ouverture des routes HTTP."""
    logger.info("Initialisation du cycle de vie FastAPI.")

    # Les tests unitaires n'ont pas besoin d'un vrai stockage MinIO ni d'un vrai
    # chargement de modele. Cette variable permet d'isoler les tests du runtime.
    if os.getenv("SKIP_MINIO_STARTUP", "0") == "1":
        logger.info(
            "Mode test detecte : initialisation MinIO et chargement du modele ignores."
        )
        yield
        logger.info("Fermeture du cycle de vie FastAPI en mode test.")
        return

    # Etape 1 : recuperer le modele de reference depuis MinIO vers le filesystem
    # local du conteneur backend.
    try:
        logger.info("Demarrage du telechargement du modele depuis MinIO.")
        model_path = download_model_from_s3()
        logger.info("Modele telecharge et pret a etre charge depuis : %s", model_path)
    except Exception as exc:
        logger.error("Echec critique pendant le telechargement du modele : %s", exc)
        raise RuntimeError(
            f"L'application ne peut pas demarrer sans modele : {exc}"
        ) from exc

    # Etape 2 : precharger le pipeline sklearn en memoire afin de faire echouer
    # le demarrage le plus tot possible en cas de modele corrompu ou incompatible.
    try:
        logger.info("Demarrage du pre-chargement du modele en memoire.")
        get_model()
        logger.info("Modele pre-charge en memoire avec succes.")
    except Exception as exc:
        logger.error("Echec critique pendant le pre-chargement du modele : %s", exc)
        raise RuntimeError(
            f"L'application ne peut pas demarrer sans modele : {exc}"
        ) from exc

    logger.info("Application prete a accepter des requetes.")
    yield
    logger.info("Fermeture du cycle de vie FastAPI.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def index():
    """Retourne un point d'entree lisible pour un utilisateur humain."""
    logger.info("Requete recue sur '/'.")
    return {"message": "ML Housing Prediction API", "docs": "/docs"}


@app.get("/health")
def health():
    """Expose un controle de sante minimal pour la supervision."""
    logger.info("Requete de sante recue sur '/health'.")
    return {"status": "ok"}


@app.post("/predict")
def predict(data: HousingFeatures):
    """Calcule une prediction de prix a partir du schema public de l'API."""
    payload = data.model_dump()
    logger.info(
        "Requete de prediction recue. champs=%s",
        ", ".join(sorted(payload.keys())),
    )
    prediction = make_prediction(payload)
    logger.info("Prediction calculee avec succes : %s", prediction)
    return {"prediction": prediction}
