from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ml import data
from pydantic import BaseModel
import pandas as pd
import joblib
from datetime import datetime

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

def get_climate_baseline(lat, lon, years=None):

    if years is None:
        current_year = datetime.now().year
        years = range(current_year - 5, current_year)  # last 5 full years

    weather_list = []

    for y in years:
        w = get_weather_data(
            lat,
            lon,
            f"{y}-04-01",
            f"{y}-09-30"
        )

        if w:
            weather_list.append(w)

    if not weather_list:
        return None

    return {
        "avg_temp": sum(w["avg_temp"] for w in weather_list) / len(weather_list),
        "total_rain": sum(w["total_rain"] for w in weather_list) / len(weather_list),
        "avg_wind": sum(w["avg_wind"] for w in weather_list) / len(weather_list),
    }


@app.post("/predict-yield")
def predict_yield(data: YieldRequest):

    years = list(range(2015, 2023))

    state = data.location.upper()
    crop = data.crop.upper()

    if state not in STATE_COORDS:
        raise HTTPException(status_code=400, detail="Invalid state code")

    lat, lon = STATE_COORDS[state]

    weather = get_climate_baseline(lat, lon)

    if weather is None:
        raise HTTPException(status_code=500, detail="Weather API failed")

    # normalize inputs
    crop = data.crop.upper()
    state = data.location.upper()

    # start clean feature dict
    row = {col: 0 for col in feature_cols}

    # numeric features
    row["year"] = datetime.now().year
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

    training_df = pd.read_csv("ml/data/training_data.csv")

    state_col = f"state_{data.location}"
    crop_col = f"crop_{data.crop}"

    historical = (
        training_df[
            (training_df[state_col] == 1) &
            (training_df[crop_col] == 1)
        ]
        .groupby("year", as_index=False)["yield"]
        .mean()
        .sort_values("year")
    )

    historical_avg = historical["yield"].mean()

    recent_years = historical.tail(10).to_dict(orient="records")

    return {
        "predicted_yield": float(prediction),
        "historical_avg": round(float(historical_avg), 2) if not pd.isna(historical_avg) else None,
        "historical_data": recent_years
    }