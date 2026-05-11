"""Point d'entree principal pour entrainer un modele localement."""

import logging
import shutil
from pathlib import Path

from src.training.pipeline import get_next_version, run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Demarrage du pipeline principal d'entrainement.")
    version = get_next_version()
    logger.info("Prochaine version de modele calculee : %s", version)

    metrics = run_pipeline(version=version)
    logger.info("Pipeline termine avec les metriques suivantes : %s", metrics)

    print("Pipeline termine avec succes.")
    print(f"Version : {version}")
    print(f"MAE  : {metrics['mae']:.4f}")
    print(f"RMSE : {metrics['rmse']:.4f}")
    print(f"R2   : {metrics['r2']:.4f}")

    # Cette synchronisation maintient une convention de nommage stable pour
    # le backend et pour le script d'upload vers MinIO.
    model_dir = Path("artifacts/models")
    new_model = model_dir / f"model_{version}.joblib"
    legacy_model = model_dir / f"model{('_' + version) if version else ''}.joblib"
    latest_model = model_dir / "model_latest.joblib"

    # Le pipeline sauvegarde actuellement sous la forme `model_vX.joblib`.
    # Cette logique relie explicitement le nom versionne attendu au nom latest.
    source_model = legacy_model if legacy_model.exists() else new_model

    if source_model.exists():
        logger.info("Copie du modele %s vers %s", source_model, latest_model)
        shutil.copy(source_model, latest_model)
        print(f"Modele 'latest' synchronise : {latest_model}")
    else:
        logger.warning("Le modele versionne attendu est introuvable : %s", source_model)
