from fastapi import FastAPI
from src.prediction.schemas import HousingFeatures
from src.prediction.predict import make_prediction

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: HousingFeatures):
    # Appel du service de prédiction découplé
    prediction = make_prediction(data.model_dump())
    return {"prediction": prediction}
