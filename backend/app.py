import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI

from backend.services.ab_router import choose_variant
from backend.services.experiment_logger import log_prediction
from backend.services.model_registry import MODEL_VERSIONS, get_models
from src.prediction.model_loader import get_model
from src.prediction.predict import make_prediction, normalize_prediction_features
from src.prediction.schemas import HousingFeatures

# Le backend reutilise le logger uvicorn afin de centraliser les logs applicatifs
# dans la meme sortie que les logs HTTP lorsque l'application tourne dans Docker.
logger = logging.getLogger("uvicorn.error")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
RUNNING_IN_DOCKER = os.path.exists("/.dockerenv")
LOCAL_MODEL_PATH_DEFAULT = os.path.join(
    PROJECT_ROOT, "artifacts", "models", "model_latest.joblib"
)

if not RUNNING_IN_DOCKER and os.getenv("LOCAL_MODEL_PATH", "").startswith("/app/"):
    os.environ["LOCAL_MODEL_PATH"] = LOCAL_MODEL_PATH_DEFAULT

DEFAULT_TRAFFIC_B_PERCENT = int(os.getenv("AB_TRAFFIC_B_PERCENT", "50"))
REQUIRE_AB_MODELS = os.getenv("REQUIRE_AB_MODELS", "0") == "1"


def predict_with_experiment(payload: dict) -> tuple[float, dict]:
    """
    Exécute l'inférence en utilisant le routage A/B si disponible,
    sinon bascule sur le modèle legacy.

    Cette fonction centralise la logique métier de l'expérimentation :
    1. Attribution d'un ID de requête unique.
    2. Sélection de la variante (A ou B) via le ab_router.
    3. Tentative de prédiction via le registre de modèles (A/B).
    4. Repli (fallback) sur la fonction de prédiction unifiée en cas d'erreur.
    5. Journalisation complète de l'événement pour analyse ultérieure.
    """
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    user_id = payload.get("user_id") or "anonymous"
    features_only = {
        feature_name: feature_value
        for feature_name, feature_value in payload.items()
        if feature_name != "user_id"
    }
    variant = choose_variant(user_id, traffic_b_percent=DEFAULT_TRAFFIC_B_PERCENT)
    logger.info(
        "Variant selection complete. user_id=%s variant=%s traffic_b_percent=%s",
        user_id,
        variant,
        DEFAULT_TRAFFIC_B_PERCENT,
    )

    try:
        models = get_models()
        normalized_features = normalize_prediction_features(features_only)
        dataframe = pd.DataFrame([normalized_features])
        prediction = float(models[variant].predict(dataframe)[0])
        model_version = MODEL_VERSIONS[variant]
        execution_mode = "ab_registry"
        logger.info(
            "Prediction produced via A/B registry. variant=%s model_version=%s",
            variant,
            model_version,
        )
    except (FileNotFoundError, KeyError) as exc:
        logger.warning(
            "A/B models unavailable, fallback to legacy single-model inference. %s",
            exc,
        )
        prediction = make_prediction(features_only)
        model_version = "legacy_single_model"
        execution_mode = "legacy_fallback"
        logger.info("Prediction produced via legacy single-model pipeline.")

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    event = {
        "request_id": request_id,
        "user_id": user_id,
        "variant": variant,
        "model_version": model_version,
        "execution_mode": execution_mode,
        "prediction": prediction,
        "latency_ms": latency_ms,
        "features": features_only,
    }
    log_prediction(event)

    return prediction, event


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application FastAPI.

    S'assure que les ressources critiques (modèles depuis MinIO) sont disponibles
    avant que l'API ne commence à accepter des requêtes HTTP.
    """
    logger.info("Initialisation du cycle de vie FastAPI.")

    # Les tests unitaires n'ont pas besoin d'un vrai stockage ni d'un vrai
    # chargement de modele. Cette variable permet d'isoler les tests du runtime.
    if os.getenv("SKIP_MINIO_STARTUP", "0") == "1":
        logger.info("Mode test detecte : stockage et chargement du modele ignores.")
        yield
        logger.info("Fermeture du cycle de vie FastAPI en mode test.")
        return

    # Sélection du backend de stockage selon la présence de HF_REPO_ID.
    if os.getenv("HF_REPO_ID"):
        from backend.storage.hf_client import (
            download_ab_models_from_hf as _download_ab_models,
        )
        from backend.storage.hf_client import (
            download_model_from_hf as _download_model,
        )

        logger.info(
            "Stockage des modeles : HuggingFace Hub (repo=%s)", os.getenv("HF_REPO_ID")
        )
    else:
        from backend.storage.s3_client import (
            download_ab_models_from_s3 as _download_ab_models,
        )
        from backend.storage.s3_client import (
            download_model_from_s3 as _download_model,
        )

        logger.info("Stockage des modeles : MinIO / S3")

    # Etape 1 : recuperer le modele de reference depuis le stockage vers le filesystem
    # local du conteneur backend.
    try:
        logger.info("Demarrage du telechargement du modele principal.")
        model_path = _download_model()
        logger.info("Modele telecharge et pret a etre charge depuis : %s", model_path)
    except Exception as exc:
        logger.error("Echec critique pendant le telechargement du modele : %s", exc)
        raise RuntimeError(
            f"L'application ne peut pas demarrer sans modele : {exc}"
        ) from exc

    # Etape 2 : precharger le pipeline sklearn en memoire afin de faire echouer
    # le demarrage le plus tot possible en cas de modele corrompu ou incompatible.
    try:
        logger.info("Demarrage du pre-chargement du modele historique en memoire.")
        get_model()
        logger.info("Modele historique pre-charge en memoire avec succes.")
    except Exception as exc:
        logger.error("Echec critique pendant le pre-chargement du modele : %s", exc)
        raise RuntimeError(
            f"L'application ne peut pas demarrer sans modele : {exc}"
        ) from exc

    # Etape 3 : si les artefacts A/B existent, les precharger aussi.
    try:
        logger.info("Demarrage du telechargement des modeles A/B versionnes.")
        downloaded_ab_models = _download_ab_models()
        logger.info("Modeles A/B telecharges avec succes : %s", downloaded_ab_models)
        logger.info("Verification de la disponibilite du registry A/B.")
        get_models()
        logger.info("Registry A/B charge avec succes.")
    except FileNotFoundError as exc:
        if REQUIRE_AB_MODELS:
            logger.error("Mode A/B complet requis mais indisponible : %s", exc)
            raise RuntimeError(
                f"L'application ne peut pas demarrer en mode A/B complet : {exc}"
            ) from exc
        logger.warning(
            "Registry A/B incomplet ou absent. L'application utilisera le fallback "
            "historique tant que les deux modeles ne sont pas presents. %s",
            exc,
        )

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
        "Requete de prediction recue. user_id=%s champs=%s",
        payload.get("user_id"),
        ", ".join(sorted(payload.keys())),
    )
    prediction, event = predict_with_experiment(payload)
    logger.info(
        "Prediction calculee avec succes : %s. variant=%s mode=%s request_id=%s",
        prediction,
        event["variant"],
        event["execution_mode"],
        event["request_id"],
    )
    return {
        "prediction": prediction,
        "variant": event["variant"],
        "model_version": event["model_version"],
        "execution_mode": event["execution_mode"],
        "latency_ms": event["latency_ms"],
        "request_id": event["request_id"],
    }
