"""Data loading and preprocessing utilities."""
from sklearn.datasets import fetch_california_housing
import pandas as pd


def load_housing_data() -> pd.DataFrame:
    """Charge le dataset California Housing sous forme de DataFrame."""
    dataset = fetch_california_housing(as_frame=True)
    df = dataset.frame
    return df
