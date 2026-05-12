import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODELS_DIR = PROJECT_ROOT / "artifacts" / "models"
MODEL_FILES = {
    "model_latest.joblib": os.getenv("MODEL_OBJECT_NAME", "model_latest.joblib"),
    "model_v1.joblib": os.getenv("MODEL_A_OBJECT_NAME", "model_v1.joblib"),
    "model_v2.joblib": os.getenv("MODEL_B_OBJECT_NAME", "model_v2.joblib"),
}


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

    uploads = {
        MODELS_DIR / local_name: hf_name for local_name, hf_name in MODEL_FILES.items()
    }

    missing = [str(p) for p in uploads if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Artefacts introuvables — lancer `python main.py` d'abord :\n"
            + "\n".join(missing)
        )

    api = HfApi(token=token)
    logger.info("Upload vers HF Hub. repo=%s", repo_id)

    for local_path, hf_filename in uploads.items():
        logger.info("Upload : %s -> %s/%s", local_path.name, repo_id, hf_filename)
        api.upload_file(
            path_or_fileobj=str(local_path),
            path_in_repo=hf_filename,
            repo_id=repo_id,
            repo_type="model",
        )
        logger.info("Upload termine : %s", hf_filename)

    print(
        f"Modeles uploades vers hf://models/{repo_id} : "
        + ", ".join(MODEL_FILES.values())
    )


if __name__ == "__main__":
    main()
