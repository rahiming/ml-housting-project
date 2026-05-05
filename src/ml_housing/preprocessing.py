"""Data preprocessing utilities."""

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def get_preprocessing_pipeline() -> Pipeline:
    """Crée et retourne le pipeline de preprocessing."""
    return Pipeline(
        [
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),  # Gère les valeurs manquantes
            ("scaler", StandardScaler()),
        ]
    )
