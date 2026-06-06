from fastapi import FastAPI
from backend.app.services.weather_service import get_weather_features
from backend.app.services.crop_service import get_crop_yield_data

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

#test weather api
@app.get("/weather-test")
def weather_test():
    return get_weather_features(48.42, -122.33)

#test crop api
@app.get("/crop-test")
def crop_test():
    return get_crop_yield_data("CORN", "WA", "2015").head().to_dict()