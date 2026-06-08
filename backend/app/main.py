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

    state = data.location.upper()
    crop = data.crop.upper()

    if state not in STATE_COORDS:
        raise HTTPException(status_code=400, detail="Invalid state code")

    lat, lon = STATE_COORDS[state]

    weather = get_weather_data(
        lat,
        lon,
        f"{data.year}-04-01",
        f"{data.year}-09-30"
    )

    if not weather:
        raise HTTPException(status_code=500, detail="Weather API failed")

    # normalize inputs
    crop = data.crop.upper()
    state = data.location.upper()

    # start clean feature dict
    row = {col: 0 for col in feature_cols}

    # numeric features
    row["year"] = data.year
    row["avg_temp"] = weather["avg_temp"]
    row["total_rain"] = weather["total_rain"]
    row["avg_wind"] = weather["avg_wind"]

    # one-hot features
    state_col = f"state_{state}"
    crop_col = f"crop_{crop}"

    if state_col in row:
        row[state_col] = 1

    if crop_col in row:
        row[crop_col] = 1

    features = pd.DataFrame([row])[feature_cols]

    prediction = model.predict(features)[0]

    print(f"{crop} {state} {data.year} -> {prediction:.2f}")

    return {"predicted_yield": float(prediction)}