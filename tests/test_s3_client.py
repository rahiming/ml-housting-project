import os
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from backend.storage.s3_client import (
    download_model_from_s3,
    ensure_bucket_exists,
    get_s3_client,
    wait_for_minio,
)

MOCK_ENV_VARS = {
    "MINIO_ENDPOINT": "http://mock-minio:9000",
    "MINIO_ACCESS_KEY": "mock_access",
    "MINIO_SECRET_KEY": "mock_secret",
    "MINIO_BUCKET_MODELS": "mock-bucket",
    "MODEL_OBJECT_NAME": "mock_model.joblib",
    "LOCAL_MODEL_PATH": "artifacts/mock_model.joblib",
}


@patch.dict(os.environ, MOCK_ENV_VARS)
@patch("backend.storage.s3_client.boto3.client")
def test_get_s3_client(mock_boto_client):
    """Test that get_s3_client calls boto3.client with correct parameters."""
    get_s3_client()
    mock_boto_client.assert_called_once_with(
        "s3",
        endpoint_url=MOCK_ENV_VARS["MINIO_ENDPOINT"],
        aws_access_key_id=MOCK_ENV_VARS["MINIO_ACCESS_KEY"],
        aws_secret_access_key=MOCK_ENV_VARS["MINIO_SECRET_KEY"],
    )


@patch.dict(os.environ, MOCK_ENV_VARS)
@patch("backend.storage.s3_client.time.sleep")
@patch("backend.storage.s3_client.boto3.client")
def test_wait_for_minio_success_first_attempt(mock_boto_client, mock_sleep):
    """Test wait_for_minio succeeds on the first attempt."""
    mock_s3_client = MagicMock()
    mock_boto_client.return_value = mock_s3_client
    mock_s3_client.list_buckets.return_value = {"Buckets": []}

    s3_client = wait_for_minio(max_retries=1)
    assert s3_client == mock_s3_client
    mock_s3_client.list_buckets.assert_called_once()
    mock_sleep.assert_not_called()


@patch.dict(os.environ, MOCK_ENV_VARS)
@patch("backend.storage.s3_client.time.sleep")
@patch("backend.storage.s3_client.boto3.client")
def test_wait_for_minio_success_after_retries(mock_boto_client, mock_sleep):
    """Test wait_for_minio succeeds after a few retries."""
    mock_s3_client = MagicMock()
    mock_boto_client.return_value = mock_s3_client
    mock_s3_client.list_buckets.side_effect = [
        Exception("Error"),
        Exception("Error"),
        {"Buckets": []},
    ]

    s3_client = wait_for_minio(max_retries=3, delay=0.01)
    assert s3_client == mock_s3_client
    assert mock_s3_client.list_buckets.call_count == 3
    assert mock_sleep.call_count == 2


@patch.dict(os.environ, MOCK_ENV_VARS)
@patch("backend.storage.s3_client.time.sleep")
@patch("backend.storage.s3_client.boto3.client")
def test_wait_for_minio_failure_after_max_retries(mock_boto_client, mock_sleep):
    """Test wait_for_minio raises RuntimeError after max retries."""
    mock_s3_client = MagicMock()
    mock_boto_client.return_value = mock_s3_client
    mock_s3_client.list_buckets.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match="MinIO n'est pas disponible"):
        wait_for_minio(max_retries=2, delay=0.01)
    assert mock_s3_client.list_buckets.call_count == 2
    assert mock_sleep.call_count == 2


@patch.dict(os.environ, MOCK_ENV_VARS)
@patch("backend.storage.s3_client.wait_for_minio")
def test_ensure_bucket_exists_already_exists(mock_wait_for_minio):
    """Test ensure_bucket_exists when the bucket already exists."""
    mock_s3_client = MagicMock()
    mock_wait_for_minio.return_value = mock_s3_client
    mock_s3_client.list_buckets.return_value = {
        "Buckets": [{"Name": MOCK_ENV_VARS["MINIO_BUCKET_MODELS"]}]
    }

    s3_client = ensure_bucket_exists(MOCK_ENV_VARS["MINIO_BUCKET_MODELS"])
    assert s3_client == mock_s3_client
    mock_s3_client.list_buckets.assert_called_once()
    mock_s3_client.create_bucket.assert_not_called()


@patch.dict(os.environ, MOCK_ENV_VARS)
@patch("backend.storage.s3_client.wait_for_minio")
def test_ensure_bucket_exists_creates_bucket(mock_wait_for_minio):
    """Test ensure_bucket_exists when the bucket needs to be created."""
    mock_s3_client = MagicMock()
    mock_wait_for_minio.return_value = mock_s3_client
    mock_s3_client.list_buckets.return_value = {"Buckets": []}

    s3_client = ensure_bucket_exists(MOCK_ENV_VARS["MINIO_BUCKET_MODELS"])
    assert s3_client == mock_s3_client
    mock_s3_client.list_buckets.assert_called_once()
    mock_s3_client.create_bucket.assert_called_once_with(
        Bucket=MOCK_ENV_VARS["MINIO_BUCKET_MODELS"]
    )


@patch.dict(os.environ, MOCK_ENV_VARS)
@patch("backend.storage.s3_client.os.makedirs")
@patch("backend.storage.s3_client.ensure_bucket_exists")
def test_download_model_from_s3_success(mock_ensure_bucket_exists, mock_makedirs):
    """Test download_model_from_s3 successfully downloads a model."""
    mock_s3_client = MagicMock()
    mock_ensure_bucket_exists.return_value = mock_s3_client

    local_path = download_model_from_s3()
    mock_makedirs.assert_called_once_with(
        os.path.dirname(MOCK_ENV_VARS["LOCAL_MODEL_PATH"]), exist_ok=True
    )
    mock_s3_client.download_file.assert_called_once_with(
        MOCK_ENV_VARS["MINIO_BUCKET_MODELS"],
        MOCK_ENV_VARS["MODEL_OBJECT_NAME"],
        MOCK_ENV_VARS["LOCAL_MODEL_PATH"],
    )
    assert local_path == MOCK_ENV_VARS["LOCAL_MODEL_PATH"]


@patch.dict(os.environ, {}, clear=True)
def test_download_model_from_s3_missing_bucket_env_var():
    """Test download_model_from_s3 raises ValueError if bucket env var is missing."""
    with pytest.raises(ValueError, match="MINIO_BUCKET_MODELS est manquante"):
        download_model_from_s3()


@patch.dict(os.environ, {"MINIO_BUCKET_MODELS": "test-bucket"}, clear=True)
def test_download_model_from_s3_missing_object_env_var():
    """Test download_model_from_s3 raises ValueError if object env var is missing."""
    with pytest.raises(ValueError, match="MODEL_OBJECT_NAME est manquante"):
        download_model_from_s3()


@patch.dict(os.environ, MOCK_ENV_VARS)
@patch("backend.storage.s3_client.os.makedirs")
@patch("backend.storage.s3_client.ensure_bucket_exists")
def test_download_model_from_s3_not_found_error(
    mock_ensure_bucket_exists, mock_makedirs
):
    """Test download_model_from_s3 raises FileNotFoundError on 404 ClientError."""
    mock_s3_client = MagicMock()
    mock_ensure_bucket_exists.return_value = mock_s3_client
    mock_s3_client.download_file.side_effect = ClientError(
        {"Error": {"Code": "404"}}, "HeadObject"
    )

    with pytest.raises(FileNotFoundError, match="Impossible de t"):
        download_model_from_s3()
