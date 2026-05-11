import logging
import os
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

# Ce module est execute pendant le demarrage du backend. Il utilise donc
# le logger uvicorn afin que tous les evenements soient visibles dans
# `docker compose logs backend`.
logger = logging.getLogger("uvicorn.error")


def get_s3_client():
    """Construit un client S3 compatible MinIO a partir de l'environnement."""
    endpoint_url = os.getenv("MINIO_ENDPOINT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")

    logger.info(
        (
            "Creation du client MinIO. endpoint=%s access_key_present=%s "
            "secret_key_present=%s"
        ),
        endpoint_url,
        bool(access_key),
        bool(secret_key),
    )

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def wait_for_minio(max_retries: int = 10, delay: int = 2):
    """Attend que MinIO reponde avant de poursuivre le demarrage."""
    logger.info(
        "Attente de disponibilite de MinIO. max_retries=%s delay=%s",
        max_retries,
        delay,
    )
    s3 = get_s3_client()

    for attempt in range(1, max_retries + 1):
        try:
            s3.list_buckets()
            logger.info("MinIO est disponible.")
            return s3
        except Exception as exc:
            logger.warning(
                "MinIO indisponible, tentative %s/%s : %s",
                attempt,
                max_retries,
                exc,
            )
            time.sleep(delay)

    logger.error("MinIO indisponible apres %s tentatives.", max_retries)
    raise RuntimeError("MinIO n'est pas disponible apres plusieurs tentatives.")


def ensure_bucket_exists(bucket_name: str):
    """Cree le bucket cible s'il n'existe pas deja."""
    logger.info("Verification de l'existence du bucket '%s'.", bucket_name)
    s3 = wait_for_minio()

    existing_buckets = s3.list_buckets().get("Buckets", [])
    existing_bucket_names = [bucket["Name"] for bucket in existing_buckets]
    logger.info("Buckets actuellement visibles : %s", existing_bucket_names)

    if bucket_name not in existing_bucket_names:
        s3.create_bucket(Bucket=bucket_name)
        logger.info("Bucket cree : %s", bucket_name)
    else:
        logger.info("Le bucket '%s' existe deja.", bucket_name)

    return s3


def download_model_from_s3():
    """Telecharge le modele de production depuis MinIO vers le backend local."""
    bucket_name = os.getenv("MINIO_BUCKET_MODELS")
    object_name = os.getenv("MODEL_OBJECT_NAME")
    local_model_path = os.getenv(
        "LOCAL_MODEL_PATH", "/app/artifacts/models/model_latest.joblib"
    )

    return download_named_model_from_s3(bucket_name, object_name, local_model_path)


def download_named_model_from_s3(
    bucket_name: str, object_name: str, local_model_path: str
):
    """Download one named model object from MinIO to a local filesystem path."""

    logger.info(
        "Preparation du telechargement du modele. bucket=%s object=%s local_path=%s",
        bucket_name,
        object_name,
        local_model_path,
    )

    if not bucket_name:
        logger.error("Variable manquante : MINIO_BUCKET_MODELS")
        raise ValueError("La variable MINIO_BUCKET_MODELS est manquante.")

    if not object_name:
        logger.error("Variable manquante : MODEL_OBJECT_NAME")
        raise ValueError("La variable MODEL_OBJECT_NAME est manquante.")

    target_dir = os.path.dirname(local_model_path)
    logger.info("Verification du repertoire local de destination : %s", target_dir)
    os.makedirs(target_dir, exist_ok=True)

    s3 = ensure_bucket_exists(bucket_name)

    try:
        logger.info(
            "Telechargement de l'objet s3://%s/%s vers %s",
            bucket_name,
            object_name,
            local_model_path,
        )
        s3.download_file(bucket_name, object_name, local_model_path)
        logger.info(
            "Modele telecharge depuis MinIO : s3://%s/%s",
            bucket_name,
            object_name,
        )
        return local_model_path
    except ClientError as exc:
        logger.error(
            "Echec du telechargement du modele. bucket=%s object=%s error=%s",
            bucket_name,
            object_name,
            exc,
        )
        raise FileNotFoundError(
            f"Impossible de telecharger le modele s3://{bucket_name}/{object_name}. "
            "Verifier que le fichier model_latest.joblib a bien ete upload dans MinIO."
        ) from exc


def download_ab_models_from_s3() -> dict:
    """Download the versioned A/B models required by the experiment registry."""
    bucket_name = os.getenv("MINIO_BUCKET_MODELS")
    base_models_dir = Path(
        os.getenv("LOCAL_MODEL_PATH", "/app/artifacts/models/model_latest.joblib")
    ).parent
    model_a_path = os.getenv(
        "MODEL_A_LOCAL_PATH", str(base_models_dir / "model_v1.joblib")
    )
    model_b_path = os.getenv(
        "MODEL_B_LOCAL_PATH", str(base_models_dir / "model_v2.joblib")
    )
    model_a_object = os.getenv("MODEL_A_OBJECT_NAME", "model_v1.joblib")
    model_b_object = os.getenv("MODEL_B_OBJECT_NAME", "model_v2.joblib")

    logger.info(
        (
            "Preparation du telechargement des modeles A/B. bucket=%s "
            "model_a=%s model_b=%s"
        ),
        bucket_name,
        model_a_object,
        model_b_object,
    )

    return {
        "A": download_named_model_from_s3(bucket_name, model_a_object, model_a_path),
        "B": download_named_model_from_s3(bucket_name, model_b_object, model_b_path),
    }
