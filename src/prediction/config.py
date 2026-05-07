import os
from pathlib import Path

# Calcul dynamique de la racine du projet (ML-HOUSING-PROJECT/)
# Ce fichier étant dans src/prediction/, on remonte de 3 niveaux
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Dossier des artefacts (utilisé par le backend et le pipeline)
# On autorise une surcharge par variable d'environnement (pratique pour Docker/K8s)
ARTIFACTS_PATH = Path(os.getenv("ARTIFACTS_PATH", PROJECT_ROOT / "artifacts"))
MODELS_PATH = ARTIFACTS_PATH / "models"

# Noms de fichiers standards pour la production
MODEL_LATEST_NAME = "model_latest.joblib"
MODEL_VERSION_PATTERN = "model_v*.joblib"
