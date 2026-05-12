"""Orchestration du pipeline ML d'entrainement et de sauvegarde."""

import json
import logging
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn

from src.common.features import split_features_target, split_train_test
from src.training.data import load_housing_data
from src.training.evaluate import evaluate_model
from src.training.train import train_model

logger = logging.getLogger(__name__)

MLFLOW_EXPERIMENT = "housing_price_prediction"


def get_next_version(artifacts_dir: str = "artifacts") -> str:
    """Calcule la prochaine version de modele disponible."""
    path = Path(artifacts_dir).resolve()
    models_path = path / "models"
    logger.info("Calcul de la prochaine version dans %s", models_path)

    if not models_path.exists():
        logger.info("Dossier models absent. La premiere version sera v1.")
        return "v1"

    existing_versions = []
    for model_file in models_path.glob("model_v*.joblib"):
        try:
            version_number = int(model_file.stem.split("_v")[-1])
            existing_versions.append(version_number)
        except (ValueError, IndexError):
            logger.warning("Nom de modele ignore car non conforme : %s", model_file)
            continue

    next_version = max(existing_versions, default=0) + 1
    logger.info("Prochaine version calculee : v%s", next_version)
    return f"v{next_version}"


def run_pipeline(artifacts_dir: str = "artifacts", version: str = "") -> dict:
    """Execute le pipeline complet avec tracking MLFlow."""
    artifacts_path = Path(artifacts_dir).resolve()
    models_path = artifacts_path / "models"
    metrics_path = artifacts_path / "metrics"
    logger.info(
        "Demarrage du pipeline local. artifacts=%s version=%s",
        artifacts_path,
        version,
    )

    models_path.mkdir(parents=True, exist_ok=True)
    metrics_path.mkdir(parents=True, exist_ok=True)

    df = load_housing_data()
    logger.info("Dataset charge. lignes=%s colonnes=%s", len(df), len(df.columns))

    X, y = split_features_target(df)
    logger.info("Separation des variables effectuee. features=%s", list(X.columns))

    X_train, X_test, y_train, y_test = split_train_test(X, y)
    logger.info(
        "Split train/test termine. X_train=%s X_test=%s",
        X_train.shape,
        X_test.shape,
    )

    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    with mlflow.start_run(run_name=f"run_{version}" if version else None):
        mlflow.log_param("model_type", "RandomForestRegressor")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("random_state", 42)
        mlflow.log_param("version", version or "latest")
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))

        model = train_model(X_train, y_train)
        logger.info("Modele entraine avec succes.")

        metrics = evaluate_model(model, X_test, y_test)
        mlflow.log_metric("mae", metrics["mae"])
        mlflow.log_metric("rmse", metrics["rmse"])
        mlflow.log_metric("r2", metrics["r2"])
        logger.info("Evaluation terminee. metrics=%s", metrics)

        suffix = f"_{version}" if version else ""
        model_file = models_path / f"model{suffix}.joblib"
        metrics_file = metrics_path / f"metrics{suffix}.json"

        joblib.dump(model, model_file)
        logger.info("Sauvegarde du modele versionne dans %s", model_file)

        latest_path = models_path / "model_latest.joblib"
        joblib.dump(model, latest_path)
        logger.info("Sauvegarde de la copie latest dans %s", latest_path)

        with open(metrics_file, "w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=2)
        logger.info("Metriques enregistrees dans %s", metrics_file)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=f"housing_{version}" if version else "housing_latest",
        )
        mlflow.log_artifact(str(metrics_file), artifact_path="metrics")
        logger.info("Run MLFlow enregistre avec succes.")

    return metrics
