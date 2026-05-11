"""Model evaluation utilities."""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_model(model, X_test, y_test) -> dict:
    """Évalue le modèle et retourne les métriques principales."""
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }
