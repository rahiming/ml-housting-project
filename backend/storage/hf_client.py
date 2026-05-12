import logging
import os

from huggingface_hub import hf_hub_download

logger = logging.getLogger("uvicorn.error")


def _repo_id() -> str:
    repo_id = os.getenv("HF_REPO_ID", "")
    if not repo_id:
        raise ValueError("La variable HF_REPO_ID est manquante.")
    return repo_id


def _token() -> str | None:
    return os.getenv("HF_TOKEN") or None


def _download_file(filename: str, local_path: str) -> str:
    repo_id = _repo_id()
    token = _token()
    local_dir = os.path.dirname(local_path)
    os.makedirs(local_dir, exist_ok=True)

    logger.info(
        "Telechargement depuis HF Hub. repo=%s filename=%s -> %s",
        repo_id,
        filename,
        local_path,
    )

    hf_hub_download(  # nosec B615 — dépôt privé sous notre contrôle
        repo_id=repo_id,
        filename=filename,
        repo_type="model",
        token=token,
        local_dir=local_dir,
    )

    logger.info("Telechargement HF Hub termine : %s", local_path)
    return local_path


def download_model_from_hf() -> str:
    object_name = os.getenv("MODEL_OBJECT_NAME", "model_latest.joblib")
    local_path = os.getenv(
        "LOCAL_MODEL_PATH", "/app/artifacts/models/model_latest.joblib"
    )
    return _download_file(object_name, local_path)


def download_ab_models_from_hf() -> dict:
    base_dir = os.path.dirname(
        os.getenv("LOCAL_MODEL_PATH", "/app/artifacts/models/model_latest.joblib")
    )
    model_a_object = os.getenv("MODEL_A_OBJECT_NAME", "model_v1.joblib")
    model_b_object = os.getenv("MODEL_B_OBJECT_NAME", "model_v2.joblib")
    model_a_path = os.getenv(
        "MODEL_A_LOCAL_PATH", os.path.join(base_dir, "model_v1.joblib")
    )
    model_b_path = os.getenv(
        "MODEL_B_LOCAL_PATH", os.path.join(base_dir, "model_v2.joblib")
    )

    return {
        "A": _download_file(model_a_object, model_a_path),
        "B": _download_file(model_b_object, model_b_path),
    }
