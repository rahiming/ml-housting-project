"""Tests pour le module de preprocessing."""

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from ml_housing.preprocessing import get_preprocessing_pipeline


def test_get_preprocessing_pipeline_returns_pipeline():
    """Vérifie que la fonction retourne bien un objet Pipeline avec les étapes attendues."""
    pipeline = get_preprocessing_pipeline()
    assert isinstance(pipeline, Pipeline)

    steps = [name for name, _ in pipeline.steps]
    assert "imputer" in steps
    assert "scaler" in steps


def test_preprocessing_pipeline_execution():
    """Vérifie que le pipeline traite les NaNs et normalise les données."""
    pipeline = get_preprocessing_pipeline()

    # Données de test : feat1 a un NaN, feat2 a des échelles différentes
    data = pd.DataFrame({"feat1": [10.0, np.nan, 30.0], "feat2": [1.0, 2.0, 3.0]})

    transformed = pipeline.fit_transform(data)

    assert transformed.shape == (3, 2)
    assert not np.isnan(transformed).any()  # Plus de valeurs manquantes
    assert np.allclose(transformed.mean(axis=0), 0, atol=1e-7)  # Données centrées
