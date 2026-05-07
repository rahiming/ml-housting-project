import logging
import os
import time
from pathlib import Path

import boto3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

MODEL_LOCAL_PATH = Path("artifacts/models/model_latest.joblib")


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
    """Publie le modele latest local dans le bucket MinIO de reference."""
    bucket_name = os.getenv("MINIO_BUCKET_MODELS", "ml-models")
    object_name = os.getenv("MODEL_OBJECT_NAME", "model_latest.joblib")
    logger.info(
        "Preparation de l'upload. local_path=%s bucket=%s object=%s",
        MODEL_LOCAL_PATH,
        bucket_name,
        object_name,
    )

    if not MODEL_LOCAL_PATH.exists():
        logger.error(
            "Le modele local a uploader est introuvable : %s",
            MODEL_LOCAL_PATH,
        )
        raise FileNotFoundError(
            f"Modele introuvable : {MODEL_LOCAL_PATH}. "
            "Verifier que l'entrainement a bien genere model_latest.joblib."
        )

    s3 = get_s3_client()
    wait_for_minio(s3)
    ensure_bucket_exists(s3, bucket_name)

    logger.info("Demarrage de l'upload vers MinIO.")
    s3.upload_file(str(MODEL_LOCAL_PATH), bucket_name, object_name)
    logger.info("Upload termine avec succes.")

    print(f"Modele uploade : {MODEL_LOCAL_PATH} -> s3://{bucket_name}/{object_name}")


if __name__ == "__main__":
    main()
