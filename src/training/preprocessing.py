"""Data preprocessing utilities."""

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src.common.features import engineer_features, engineer_features_names


def get_preprocessing_pipeline() -> Pipeline:
    """Crée et retourne le pipeline de preprocessing."""
    pipeline = Pipeline(
        [
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),  # Gère les valeurs manquantes
            (
                "engineer",
                FunctionTransformer(
                    engineer_features, feature_names_out=engineer_features_names
                ),
            ),
            ("scaler", StandardScaler()),
        ]
    )
    return pipeline.set_output(transform="pandas")
