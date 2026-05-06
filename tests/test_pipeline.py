from src.training.pipeline import get_next_version, run_pipeline


def test_pipeline_returns_metrics(tmp_path):
    metrics = run_pipeline(artifacts_dir=str(tmp_path))

    assert "mae" in metrics
    assert "rmse" in metrics
    assert "r2" in metrics
    assert metrics["mae"] > 0
    assert -1 <= metrics["r2"] <= 1
    assert (tmp_path / "model.joblib").exists()
    assert (tmp_path / "metrics.json").exists()


def test_get_next_version_logic(tmp_path):
    """Vérifie que le numéro de version s'incrémente correctement."""
    assert get_next_version(str(tmp_path)) == "v1"

    (tmp_path / "model_v1.joblib").touch()
    assert get_next_version(str(tmp_path)) == "v2"
