from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# CACHED WEATHER (NO API CALLS)
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

    # validate county exists
    key = (state, county)
    if key not in COUNTY_COORDS:
        raise HTTPException(status_code=400, detail="Invalid state/county")

    # -------------------------
    # GET WEATHER FROM CACHE
    # -------------------------
    weather_row = weather_df[
        (weather_df["state"].str.upper() == state) &
        (weather_df["county"].str.upper() == county)
    ]

    if weather_row.empty:
        raise HTTPException(status_code=500, detail="No cached weather data found")

    weather = weather_row.iloc[-1]

    # -------------------------
    # BUILD MODEL INPUT
    # -------------------------
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

    # -------------------------
    # HISTORICAL DATA (SAFE)
    # -------------------------
    yield_df = pd.read_csv("ml/data/yield_data.csv")

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

    return {
        "predicted_yield": float(prediction),
        "historical_avg": float(grouped["yield"].mean()) if not grouped.empty else None,
        "historical_data": grouped.tail(10).to_dict(orient="records")
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