import logging
import os
import time
from pathlib import Path

import boto3
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL_UPLOADS = {
    "model_latest.joblib": os.getenv("MODEL_OBJECT_NAME", "model_latest.joblib"),
    "model_v1.joblib": os.getenv("MODEL_A_OBJECT_NAME", "model_v1.joblib"),
    "model_v2.joblib": os.getenv("MODEL_B_OBJECT_NAME", "model_v2.joblib"),
}
MODELS_DIR = PROJECT_ROOT / "artifacts" / "models"


def get_s3_client():
    """Construit le client utilise pour les operations d'upload MinIO."""
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    logger.info("Creation du client MinIO local. endpoint=%s", endpoint)
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "admin"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "password123"),
    )


def wait_for_minio(s3, max_retries=10, delay=2):
    """Attend que MinIO soit disponible avant d'uploader le modele."""
    logger.info(
        "Attente de MinIO avant upload. max_retries=%s delay=%s",
        max_retries,
        delay,
    )
    for attempt in range(1, max_retries + 1):
        try:
            s3.list_buckets()
            logger.info("MinIO est joignable.")
            return
        except Exception as exc:
            logger.warning(
                "MinIO indisponible, tentative %s/%s : %s",
                attempt,
                max_retries,
                exc,
            )
            time.sleep(delay)

    logger.error("MinIO est indisponible apres toutes les tentatives.")
    raise RuntimeError("MinIO n'est pas disponible.")


def ensure_bucket_exists(s3, bucket_name):
    """Cree le bucket s'il n'est pas encore present."""
    logger.info("Verification du bucket cible '%s'.", bucket_name)
    buckets = s3.list_buckets().get("Buckets", [])
    bucket_names = [bucket["Name"] for bucket in buckets]

    if bucket_name not in bucket_names:
        s3.create_bucket(Bucket=bucket_name)
        logger.info("Bucket cree : %s", bucket_name)
    else:
        logger.info("Le bucket '%s' existe deja.", bucket_name)


def main():
    """Publie les artefacts de modele requis dans le bucket MinIO de reference."""
    bucket_name = os.getenv("MINIO_BUCKET_MODELS", "ml-models")
    uploads = {
        MODELS_DIR / local_filename: object_name
        for local_filename, object_name in MODEL_UPLOADS.items()
    }
    logger.info("Preparation de l'upload des modeles vers le bucket '%s'.", bucket_name)

    missing_files = [
        str(local_path) for local_path in uploads if not local_path.exists()
    ]
    if missing_files:
        logger.error("Artefacts locaux introuvables : %s", missing_files)
        raise FileNotFoundError(
            "Certains modeles sont introuvables. Verifier que l'entrainement A/B a "
            f"bien genere : {', '.join(missing_files)}"
        )

    s3 = get_s3_client()
    wait_for_minio(s3)
    ensure_bucket_exists(s3, bucket_name)

    for local_path, object_name in uploads.items():
        logger.info(
            "Demarrage de l'upload vers MinIO. local_path=%s object=%s",
            local_path,
            object_name,
        )
        s3.upload_file(str(local_path), bucket_name, object_name)
        logger.info("Upload termine avec succes pour : %s", object_name)

    uploaded_objects = ", ".join(MODEL_UPLOADS.values())
    print(f"Modeles uploades vers s3://{bucket_name}/ : {uploaded_objects}")


if __name__ == "__main__":
    main()
