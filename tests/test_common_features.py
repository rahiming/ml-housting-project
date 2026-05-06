import pandas as pd
from src.common.features import engineer_features


def test_engineer_features_calculation():
    """Vérifie que RoomsPerOccupancy est correctement calculé."""
    df = pd.DataFrame({"AveRooms": [10.0, 5.0], "AveOccup": [2.0, 5.0]})

    df_transformed = engineer_features(df)

    assert "RoomsPerOccupancy" in df_transformed.columns
    # 10 / 2 = 5.0
    assert df_transformed["RoomsPerOccupancy"].iloc[0] == 5.0
    # 5 / 5 = 1.0
    assert df_transformed["RoomsPerOccupancy"].iloc[1] == 1.0
