"""Feature engineering utilities."""

import pandas as pd
from sklearn.model_selection import train_test_split

TARGET_COLUMN = "MedHouseVal"


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
