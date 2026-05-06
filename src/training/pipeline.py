"""ML pipeline orchestration."""

import json
from pathlib import Path

import joblib

from src.training.data import load_housing_data
from src.common.features import split_features_target, split_train_test
from src.training.train import train_model
from src.training.evaluate import evaluate_model


def get_next_version(artifacts_dir: str = "artifacts") -> str:
    """Trouve le prochain numéro de version dans le dossier artifacts."""
    path = Path(artifacts_dir).resolve()
    if not path.exists():
        return "v1"

    existing_versions = []
    for f in path.glob("model_v*.joblib"):
        try:
            # Extrait le nombre après '_v' (ex: model_v2.joblib -> 2)
            v_num = int(f.stem.split("_v")[-1])
            existing_versions.append(v_num)
        except (ValueError, IndexError):
            continue

    next_v = max(existing_versions, default=0) + 1
    return f"v{next_v}"


def run_pipeline(artifacts_dir: str = "artifacts", version: str = "") -> dict:
    """Exécute le pipeline ML complet en local."""
    artifacts_path = Path(artifacts_dir).resolve()
    artifacts_path.mkdir(parents=True, exist_ok=True)

    df = load_housing_data()
    X, y = split_features_target(df)
    X_train, X_test, y_train, y_test = split_train_test(X, y)

    model = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)

    suffix = f"_{version}" if version else ""
    model_path = artifacts_path / f"model{suffix}.joblib"
    metrics_path = artifacts_path / f"metrics{suffix}.json"

    joblib.dump(model, model_path)
    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    return metrics
