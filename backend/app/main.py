from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.services.weather_forecast import get_weather_forecast
from backend.app.services.profit_service import calculate_profit
from pydantic import BaseModel
import pandas as pd
import joblib
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# LOAD ARTIFACTS
# -------------------------
model = joblib.load("ml/models/crop_model.pkl")
feature_cols = joblib.load("ml/models/features.pkl")
COUNTY_COORDS = joblib.load("ml/models/county_coords.pkl")

# CACHED WEATHER 
weather_df = pd.read_csv("ml/data/weather_data.csv")


class YieldRequest(BaseModel):
    state: str
    county: str
    crop: str


# -------------------------
# PREDICTION ENDPOINT
# -------------------------
@app.post("/predict-yield")
def predict_yield(req: YieldRequest):

    state = req.state.upper()
    county = req.county.upper()
    crop = req.crop.upper()

    key = (state, county)
    if key not in COUNTY_COORDS:
        raise HTTPException(status_code=400, detail="Invalid state/county")

    lat, lon = COUNTY_COORDS[key]

    # -------------------------
    # WEATHER FORECAST (FOR MODEL)
    # -------------------------
    weather = get_weather_forecast(lat, lon)

    if weather is None:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve weather forecast for {county} County, {state}"
        )

    # -------------------------
    # BUILD MODEL INPUT 
    # -------------------------
    row = {col: 0 for col in feature_cols}

    row["year"] = datetime.now().year
    row["avg_temp"] = weather["avg_temp"]
    row["total_rain"] = weather["total_rain"]
    row["avg_wind"] = weather["avg_wind"]

    state_col = f"state_{state}"
    county_col = f"county_{county}"
    crop_col = f"crop_{crop}"

    if state_col in row:
        row[state_col] = 1
    if county_col in row:
        row[county_col] = 1
    if crop_col in row:
        row[crop_col] = 1

    features = pd.DataFrame([row])[feature_cols]
    prediction = model.predict(features)[0]
    profit = calculate_profit(crop, prediction)

    # -------------------------
    # HISTORICAL YIELD DATA
    # -------------------------
    yield_df = pd.read_csv("ml/data/yield_data.csv")

    print(state, county, crop)

    yield_df["state"] = yield_df["state"].str.upper()
    yield_df["county"] = yield_df["county"].str.upper()
    yield_df["crop"] = yield_df["crop"].str.upper()

    hist = yield_df[
        (yield_df["state"] == state) &
        (yield_df["county"] == county) &
        (yield_df["crop"] == crop)
    ]

    grouped = (
        hist.groupby("year", as_index=False)["yield"]
        .mean()
        .sort_values("year")
    )

    # -------------------------
    # HISTORICAL WEATHER
    # -------------------------
    hist_weather = weather_df[
        (weather_df["state"].str.upper() == state) &
        (weather_df["county"].str.upper() == county)
    ]

    historical_weather_summary = {
        "avg_temp": hist_weather["avg_temp"].mean() if not hist_weather.empty else None,
        "total_rain": hist_weather["total_rain"].mean() if not hist_weather.empty else None,
        "avg_wind": hist_weather["avg_wind"].mean() if not hist_weather.empty else None,
    }

    # -------------------------
    # WEATHER DIFFERENCE 
    # -------------------------
    weather_anomaly = None
    if historical_weather_summary["avg_temp"] is not None:
        weather_anomaly = {
            "temp_diff": weather["avg_temp"] - historical_weather_summary["avg_temp"],
            "rain_diff": weather["total_rain"] - historical_weather_summary["total_rain"],
            "wind_diff": weather["avg_wind"] - historical_weather_summary["avg_wind"],
        }

    # -------------------------
    # FINAL RESPONSE 
    # -------------------------

    return {
        "predicted_yield": float(prediction),

        "profit": profit,

        # yield history
        "historical_yield": {
            "avg": float(grouped["yield"].mean()) if not grouped.empty else None,
            "data": grouped.tail(10).to_dict(orient="records")
        },

        # weather comparison
        "weather": {
            "forecast": weather,
            "historical_avg": historical_weather_summary
        }
    }


# -------------------------
# COUNTIES ENDPOINT
# -------------------------
@app.get("/counties/{state}")
def get_counties(state: str):

    state = state.upper()

    counties = sorted({
        county
        for (s, county) in COUNTY_COORDS.keys()
        if s == state
    })

    return {"counties": counties}