import os
from pathlib import Path

# Cette racine est calculee dynamiquement afin que les modules de prediction
# retrouvent les artefacts du projet quel que soit le point d'entree lance.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Le dossier d'artefacts centralise les modeles et les metriques. Il peut etre
# surcharge par variable d'environnement pour s'adapter a Docker ou a un autre
# environnement de deploiement.
ARTIFACTS_PATH = Path(os.getenv("ARTIFACTS_PATH", PROJECT_ROOT / "artifacts"))
MODELS_PATH = ARTIFACTS_PATH / "models"

# Convention de nommage utilisee par le backend et le pipeline d'entrainement.
MODEL_LATEST_NAME = "model_latest.joblib"
MODEL_VERSION_PATTERN = "model_v*.joblib"
