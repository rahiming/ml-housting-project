from pydantic import BaseModel


class HousingFeatures(BaseModel):
    """Schema public accepte par l'API.

    Les noms sont explicites pour l'utilisateur final. Une couche de
    normalisation se charge ensuite de convertir ces champs vers les noms
    historiques attendus par le modele sklearn.
    """

    median_income: float
    housing_median_age: float
    average_rooms: float
    average_bedrooms: float
    population: float
    average_occupancy: float
    latitude: float
    longitude: float
