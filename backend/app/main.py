from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

from backend.app.services.weather_service import get_weather_data
from backend.app.config.locationsAndCrops_config import STATE_COORDS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("ml/models/yield_model.pkl")
feature_cols = joblib.load("ml/models/features.pkl")

class YieldRequest(BaseModel):
    location: str
    crop: str
    year: int


@app.post("/predict-yield")
def predict_yield(data: YieldRequest):

    if data.location not in STATE_COORDS:
        raise HTTPException(status_code=400, detail="Invalid state code")

    lat, lon = STATE_COORDS[data.location]

    weather = get_weather_data(
        lat,
        lon,
        f"{data.year}-04-01",
        f"{data.year}-09-30"
    )

    if weather is None:
        raise HTTPException(status_code=500, detail="Weather API failed")

    row = {
        "year": data.year,
        "avg_temp": weather["avg_temp"],
        "total_rain": weather["total_rain"],
        "avg_wind": weather["avg_wind"]
    }

    # fill all features with 0
    for col in feature_cols:
        row[col] = 0

    # set correct one-hot
    state_col = f"state_{data.location}"
    crop_col = f"crop_{data.crop}"

    if state_col in feature_cols:
        row[state_col] = 1

    if crop_col in feature_cols:
        row[crop_col] = 1

    features = pd.DataFrame([row])[feature_cols]

    prediction = model.predict(features)[0]

    return {"predicted_yield": float(prediction)}