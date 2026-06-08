from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ml import data
from pydantic import BaseModel
import pandas as pd
import joblib
from datetime import datetime

from backend.app.services.weather_service import get_weather_data

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
COUNTY_COORDS = joblib.load("ml/models/county_coords.pkl")

class YieldRequest(BaseModel):
    state: str
    county: str
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

    state = data.state.upper()
    county = data.county.upper()
    crop = data.crop.upper()

    key = (state, county)

    if key not in COUNTY_COORDS:
        raise HTTPException(status_code=400, detail="Invalid state/county")

    lat, lon = COUNTY_COORDS[key]

    weather = get_climate_baseline(lat, lon)

    if weather is None:
        raise HTTPException(status_code=500, detail="Weather API failed")

    row = {col: 0 for col in feature_cols}

    row["year"] = datetime.now().year
    row["avg_temp"] = weather["avg_temp"]
    row["total_rain"] = weather["total_rain"]
    row["avg_wind"] = weather["avg_wind"]

    state_col = f"state_{state}"
    crop_col = f"crop_{crop}"

    if state_col in row:
        row[state_col] = 1

    if crop_col in row:
        row[crop_col] = 1

    features = pd.DataFrame([row])[feature_cols]

    prediction = model.predict(features)[0]

    training_df = pd.read_csv("ml/data/training_data.csv")

    state_col = f"state_{state}"
    crop_col = f"crop_{crop}"

    historical = (
        training_df[
            (training_df[state_col] == 1) &
            (training_df[crop_col] == 1)
        ]
        .groupby("year", as_index=False)["yield"]
        .mean()
        .sort_values("year")
    )

    return {
        "predicted_yield": float(prediction),
        "historical_avg": float(historical["yield"].mean()),
        "historical_data": historical.tail(10).to_dict(orient="records")
    }


@app.get("/counties/{state}")
def get_counties(state: str):
    state = state.upper()

    counties = [
        county for (s, county) in COUNTY_COORDS.keys()
        if s == state
    ]

    return {"counties": sorted(counties)}