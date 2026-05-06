"""Tests pour le module de preprocessing."""

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from ml_housing.preprocessing import get_preprocessing_pipeline


def test_get_preprocessing_pipeline_returns_pipeline():
    """Vérifie que la fonction retourne un Pipeline avec les étapes attendues."""
    pipeline = get_preprocessing_pipeline()
    assert isinstance(pipeline, Pipeline)

    steps = [name for name, _ in pipeline.steps]
    assert "imputer" in steps
    assert "scaler" in steps


def test_preprocessing_pipeline_execution():
    """Vérifie que le pipeline traite les NaNs et normalise les données."""
    pipeline = get_preprocessing_pipeline()

    # Données de test : AveRooms a un NaN, les autres sont normales
    data = pd.DataFrame(
        {
            "AveRooms": [10.0, np.nan, 30.0],
            "AveOccup": [1.0, 2.0, 3.0],
            "MedInc": [5.0, 6.0, 7.0],
        }
    )

    transformed = pipeline.fit_transform(data)

    # 3 colonnes d'origine + 1 créée (RoomsPerOccupancy) = 4
    assert transformed.shape == (3, 4)
    assert not transformed.isna().any().any()  # Plus de valeurs manquantes

    # Vérifie que la nouvelle colonne est présente
    assert "RoomsPerOccupancy" in transformed.columns

    # Vérifie que les données sont centrées (moyenne ~ 0)
    assert np.allclose(transformed.mean(axis=0), 0, atol=1e-7)  # Données centrées
