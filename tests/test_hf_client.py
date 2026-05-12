import os
from unittest.mock import patch

import pytest

from backend.storage.hf_client import (
    download_ab_models_from_hf,
    download_model_from_hf,
)

MOCK_ENV = {
    "HF_REPO_ID": "testuser/ml-models",
    "HF_TOKEN": "hf_test_token",
    "MODEL_OBJECT_NAME": "model_latest.joblib",
    "LOCAL_MODEL_PATH": "artifacts/models/model_latest.joblib",
    "MODEL_A_OBJECT_NAME": "model_v1.joblib",
    "MODEL_B_OBJECT_NAME": "model_v2.joblib",
}


@patch.dict(os.environ, MOCK_ENV)
@patch("backend.storage.hf_client.os.makedirs")
@patch("backend.storage.hf_client.hf_hub_download")
def test_download_model_from_hf_success(mock_hf_download, mock_makedirs):
    local_path = download_model_from_hf()
    expected_local_dir = os.path.dirname(MOCK_ENV["LOCAL_MODEL_PATH"])
    mock_hf_download.assert_called_once_with(
        repo_id=MOCK_ENV["HF_REPO_ID"],
        filename=MOCK_ENV["MODEL_OBJECT_NAME"],
        repo_type="model",
        token=MOCK_ENV["HF_TOKEN"],
        local_dir=expected_local_dir,
    )
    assert local_path == MOCK_ENV["LOCAL_MODEL_PATH"]


@patch.dict(os.environ, {}, clear=True)
def test_download_model_from_hf_missing_repo_id():
    with pytest.raises(ValueError, match="HF_REPO_ID"):
        download_model_from_hf()


@patch.dict(os.environ, MOCK_ENV)
@patch("backend.storage.hf_client.os.makedirs")
@patch("backend.storage.hf_client.hf_hub_download")
def test_download_ab_models_from_hf_success(mock_hf_download, mock_makedirs):
    result = download_ab_models_from_hf()
    assert set(result.keys()) == {"A", "B"}
    assert mock_hf_download.call_count == 2


@patch.dict(os.environ, MOCK_ENV)
@patch("backend.storage.hf_client.os.makedirs")
@patch("backend.storage.hf_client.hf_hub_download")
def test_download_model_from_hf_network_error(mock_hf_download, mock_makedirs):
    mock_hf_download.side_effect = Exception("Network error")
    with pytest.raises(Exception, match="Network error"):
        download_model_from_hf()
