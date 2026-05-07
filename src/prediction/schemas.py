from pydantic import BaseModel


class HousingFeatures(BaseModel):
    median_income: float
    housing_median_age: float
    average_rooms: float
    average_bedrooms: float
    population: float
    average_occupancy: float
    latitude: float
    longitude: float
