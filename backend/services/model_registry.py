from functools import lru_cache
from pathlib import Path

import joblib

MODELS_DIR = Path("artifacts/models")
MODEL_VERSIONS = {
    "A": "model_v1",
    "B": "model_v2",
}


@lru_cache(maxsize=1)
def get_models() -> dict:
    """Load and cache the A/B pipelines from local artifacts."""
    model_a_path = MODELS_DIR / "model_v1.joblib"
    model_b_path = MODELS_DIR / "model_v2.joblib"

    if not model_a_path.exists():
        raise FileNotFoundError(f"Modele A absent : {model_a_path}")
    if not model_b_path.exists():
        raise FileNotFoundError(f"Modele B absent : {model_b_path}")

    return {
        "A": joblib.load(model_a_path),  # nosec B301
        "B": joblib.load(model_b_path),  # nosec B301
    }
