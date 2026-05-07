"""Main entry point for the ML housing project."""

import shutil
from pathlib import Path

from src.training.pipeline import get_next_version, run_pipeline

if __name__ == "__main__":
    version = get_next_version()
    metrics = run_pipeline(version=version)

    print("Pipeline terminé avec succès.")
    print(f"Version : {version}")
    print(f"MAE  : {metrics['mae']:.4f}")
    print(f"RMSE : {metrics['rmse']:.4f}")
    print(f"R2   : {metrics['r2']:.4f}")

    # Mise à jour automatique du modèle 'latest' pour l'upload
    model_dir = Path("artifacts/models")
    new_model = model_dir / f"model_v{version}.joblib"
    latest_model = model_dir / "model_latest.joblib"

    if new_model.exists():
        shutil.copy(new_model, latest_model)
        print(f"✅ Modèle 'latest' synchronisé : {latest_model}")
