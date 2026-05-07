import os

# Les tests unitaires ne doivent pas dependre d'un service MinIO reel.
os.environ.setdefault("SKIP_MINIO_STARTUP", "1")
os.environ.setdefault("MINIO_ENDPOINT", "http://localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "admin")
os.environ.setdefault("MINIO_SECRET_KEY", "password123")
os.environ.setdefault("MINIO_BUCKET_MODELS", "ml-models")
os.environ.setdefault("MODEL_OBJECT_NAME", "model_latest.joblib")
