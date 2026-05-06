import pandas as pd

from src.prediction.model_loader import get_model


def make_prediction(data_dict: dict) -> float:
    df = pd.DataFrame([data_dict])
    prediction = get_model().predict(df)[0]
    return float(prediction)
