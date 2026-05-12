"""Upload models from MLFlow Model Registry (Production stage) to HuggingFace Hub.

Workflow:
  1. housing_model_A  @ Production  ->  model_v1.joblib   on HF Hub
  2. housing_model_B  @ Production  ->  model_v2.joblib   on HF Hub
  3. Best R² run in housing_price_prediction experiment -> model_latest.joblib

Before running this script, promote models in MLFlow:
  client.transition_model_version_stage("housing_model_A", version=1, stage="Production")
  client.transition_model_version_stage("housing_model_B", version=1, stage="Production")
"""

import logging
import os
import tempfile
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from dotenv import load_dotenv
from huggingface_hub import HfApi
from mlflow.tracking import MlflowClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", str(PROJECT_ROOT / "mlruns"))
EXPERIMENT_NAME = "housing_price_prediction"

REGISTRY_MAP = {
    "housing_model_A": os.getenv("MODEL_A_OBJECT_NAME", "model_v1.joblib"),
    "housing_model_B": os.getenv("MODEL_B_OBJECT_NAME", "model_v2.joblib"),
}
LATEST_HF_NAME = os.getenv("MODEL_OBJECT_NAME", "model_latest.joblib")


def _load_production_model(client: MlflowClient, model_name: str):
    """Load the Production-stage version of a registered model."""
    versions = client.get_latest_versions(model_name, stages=["Production"])
    if not versions:
        raise RuntimeError(
            f"Aucune version en stage 'Production' pour le modele '{model_name}'.\n"
            f"Promevoir d'abord : client.transition_model_version_stage"
            f"('{model_name}', version=X, stage='Production')"
        )
    version = versions[0]
    logger.info(
        "Chargement %s version=%s run_id=%s",
        model_name,
        version.version,
        version.run_id,
    )
    uri = f"models:/{model_name}/Production"
    return mlflow.sklearn.load_model(uri)


def _load_best_r2_model(client: MlflowClient):
    """Load the model from the run with the highest R² in the tracking experiment."""
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        raise RuntimeError(
            f"Experiment MLFlow '{EXPERIMENT_NAME}' introuvable. "
            "Lancer le pipeline d'entrainement au moins une fois."
        )
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="metrics.r2 > 0",
        order_by=["metrics.r2 DESC"],
        max_results=1,
    )
    if not runs:
        raise RuntimeError(
            f"Aucun run avec metrique r2 dans l'experiment '{EXPERIMENT_NAME}'."
        )
    best_run = runs[0]
    logger.info(
        "Meilleur run r2=%.4f run_id=%s",
        best_run.data.metrics.get("r2"),
        best_run.info.run_id,
    )
    uri = f"runs:/{best_run.info.run_id}/model"
    return mlflow.sklearn.load_model(uri)


def main():
    repo_id = os.getenv("HF_REPO_ID")
    token = os.getenv("HF_TOKEN")

    if not repo_id:
        raise ValueError(
            "HF_REPO_ID non defini. Ajouter HF_REPO_ID=<utilisateur>/<depot> dans .env"
        )
    if not token:
        raise ValueError(
            "HF_TOKEN non defini. Generer un token sur huggingface.co/settings/tokens"
        )

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()
    api = HfApi(token=token)

    logger.info("MLFlow tracking URI : %s", MLFLOW_TRACKING_URI)
    logger.info("Upload vers HF Hub. repo=%s", repo_id)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        uploads: list[tuple[Path, str]] = []

        # Load Production models from registry
        for model_name, hf_filename in REGISTRY_MAP.items():
            model = _load_production_model(client, model_name)
            local_file = tmp_path / hf_filename
            joblib.dump(model, local_file)
            uploads.append((local_file, hf_filename))
            logger.info("Serialise : %s -> %s", model_name, hf_filename)

        # Load best R² model as latest
        best_model = _load_best_r2_model(client)
        latest_file = tmp_path / LATEST_HF_NAME
        joblib.dump(best_model, latest_file)
        uploads.append((latest_file, LATEST_HF_NAME))
        logger.info("Serialise : meilleur r2 -> %s", LATEST_HF_NAME)

        # Upload all to HF Hub
        uploaded_names = []
        for local_path, hf_filename in uploads:
            logger.info("Upload : %s -> %s/%s", hf_filename, repo_id, hf_filename)
            api.upload_file(
                path_or_fileobj=str(local_path),
                path_in_repo=hf_filename,
                repo_id=repo_id,
                repo_type="model",
            )
            logger.info("Upload termine : %s", hf_filename)
            uploaded_names.append(hf_filename)

    print(f"Modeles uploades vers hf://models/{repo_id} : " + ", ".join(uploaded_names))


if __name__ == "__main__":
    main()
