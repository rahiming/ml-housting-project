import numpy as np
import pandas as pd

from src.common.features import (
    engineer_features,
    engineer_features_names,
    split_features_target,
)


def test_engineer_features_adds_column():
    # Préparation d'un DataFrame minimal
    df = pd.DataFrame(
        {"AveRooms": [10.0, 20.0], "AveOccup": [2.0, 5.0], "Other": [1, 2]}
    )

    processed = engineer_features(df)

    # Vérification de la création de la colonne
    assert "RoomsPerOccupancy" in processed.columns
    # Vérification du calcul : 10/2 = 5.0 et 20/5 = 4.0
    assert processed["RoomsPerOccupancy"].iloc[0] == 5.0
    assert processed["RoomsPerOccupancy"].iloc[1] == 4.0
    # Vérification que l'original n'est pas modifié (copie profonde)
    assert "RoomsPerOccupancy" not in df.columns


def test_engineer_features_names():
    input_cols = np.array(["feat1", "feat2"])
    output_cols = engineer_features_names(None, input_cols)
    assert "RoomsPerOccupancy" in output_cols
    assert len(output_cols) == 3


def test_split_features_target():
    df = pd.DataFrame(
        {"MedHouseVal": [100, 200], "Feature1": [1, 2], "Feature2": [3, 4]}
    )
    X, y = split_features_target(df, target_column="MedHouseVal")
    assert "MedHouseVal" not in X.columns
    assert len(y) == 2
    assert y.iloc[0] == 100
