"""Model training utilities."""

from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

from src.training.preprocessing import get_preprocessing_pipeline


def train_model(X_train, y_train) -> Pipeline:
    """Entraîne un modèle de régression."""
    # Récupération du preprocessing
    preprocessor = get_preprocessing_pipeline()

    # Création du pipeline complet
    full_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    full_pipeline.fit(X_train, y_train)
    return full_pipeline
