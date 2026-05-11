from src.training.data import load_housing_data


def test_load_housing_data_not_empty():
    df = load_housing_data()
    assert not df.empty


def test_target_column_exists():
    df = load_housing_data()
    assert "MedHouseVal" in df.columns
