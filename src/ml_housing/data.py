"""Data loading and preprocessing utilities."""

import pandas as pd
from sklearn.datasets import fetch_california_housing


def load_housing_data() -> pd.DataFrame:
    """Charge le dataset California Housing sous forme de DataFrame."""
    dataset = fetch_california_housing(as_frame=True)
    df = dataset.frame
    return df
