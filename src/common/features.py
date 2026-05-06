"""Feature engineering utilities."""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

TARGET_COLUMN = "MedHouseVal"


def engineer_features(X: pd.DataFrame) -> pd.DataFrame:
    """Logique de transformation partagée entre l'entraînement et l'inférence."""
    X = X.copy()
    # Exemple de transformation : ratio de pièces par occupation
    if "AveRooms" in X.columns and "AveOccup" in X.columns:
        X["RoomsPerOccupancy"] = X["AveRooms"] / X["AveOccup"]
    return X


def engineer_features_names(transformer, input_features):
    """Définit les noms des colonnes de sortie pour le FunctionTransformer."""
    return np.append(input_features, "RoomsPerOccupancy")


def split_features_target(df: pd.DataFrame, target_column: str = TARGET_COLUMN):
    """Sépare les variables explicatives X et la cible y."""
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return X, y


def split_train_test(X, y, test_size: float = 0.2, random_state: int = 42):
    """Découpe les données en train/test."""
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
    )
