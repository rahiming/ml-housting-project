"""Model training utilities."""
from sklearn.ensemble import RandomForestRegressor


def train_model(X_train, y_train) -> RandomForestRegressor:
    """Entraîne un modèle de régression."""
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model
