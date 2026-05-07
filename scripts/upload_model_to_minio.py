import os
import time
from pathlib import Path

import boto3

MODEL_LOCAL_PATH = Path("artifacts/models/model_latest.joblib")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "admin"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "password123"),
    )


def wait_for_minio(s3, max_retries=10, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            s3.list_buckets()
            return
        except Exception as exc:
            print(f"MinIO indisponible, tentative {attempt}/{max_retries}: {exc}")
            time.sleep(delay)

    raise RuntimeError("MinIO n'est pas disponible.")


def ensure_bucket_exists(s3, bucket_name):
    buckets = s3.list_buckets().get("Buckets", [])
    bucket_names = [bucket["Name"] for bucket in buckets]

    if bucket_name not in bucket_names:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket créé : {bucket_name}")


def main():
    bucket_name = os.getenv("MINIO_BUCKET_MODELS", "ml-models")
    object_name = os.getenv("MODEL_OBJECT_NAME", "model_latest.joblib")

    if not MODEL_LOCAL_PATH.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_LOCAL_PATH}. "
            "Vérifier que le train a bien généré le fichier model_latest.joblib."
        )

    s3 = get_s3_client()
    wait_for_minio(s3)
    ensure_bucket_exists(s3, bucket_name)

    s3.upload_file(str(MODEL_LOCAL_PATH), bucket_name, object_name)

    print(f"Modèle uploadé : {MODEL_LOCAL_PATH} -> s3://{bucket_name}/{object_name}")


if __name__ == "__main__":
    main()
