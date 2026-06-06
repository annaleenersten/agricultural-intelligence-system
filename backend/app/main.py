from fastapi import FastAPI
from backend.app.services.weather_service import get_weather_features
from backend.app.services.crop_service import get_crop_yield_data
from backend.app.services.feature_engineering import build_features
import joblib

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

model = joblib.load("ml/yield_model.pkl")

@app.get("/predict-yield")
def predict_yield(lat: float, lon: float, crop: int, state: int):
    weather = get_weather_features(lat, lon)

    features = build_features(weather, crop, state)

    prediction = model.predict([features])[0]

    return {
        "predicted_yield": prediction,
        "features_used": features
    }

# #test weather api
# @app.get("/weather-test")
# def weather_test():
#     return get_weather_features(48.42, -122.33)

# #test crop api
# @app.get("/crop-test")
# def crop_test():
#     return get_crop_yield_data("CORN", "WA", "2015").head().to_dict()