from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

from backend.app.services.weather_service import get_weather_features
from backend.app.services.crop_service import get_crop_yield_data
from backend.app.services.feature_engineering import build_features
from backend.app.config.locationsAndCrops_config import STATE_COORDS

app = FastAPI()

# --------------------
# CORS SETUP
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# ROOT TEST ROUTE
# --------------------
@app.get("/")
def home():
    return {"status": "running"}

# --------------------
# LOAD MODEL
# --------------------
model = joblib.load("ml/models/yield_model.pkl")
feature_cols = joblib.load("ml/models/features.pkl")

# --------------------
# REQUEST BODY
# --------------------
class YieldRequest(BaseModel):
    location: str
    crop: str
    year: int


@app.post("/predict-yield")
def predict_yield(data: YieldRequest):

    lat, lon = STATE_COORDS[data.location]

    if data.location not in STATE_COORDS:
        raise HTTPException(status_code=400, detail="Invalid state code")

    weather = get_weather_features(
        lat,
        lon,
        f"{data.year}-04-01",
        f"{data.year}-09-30"
    )

    row = {
        "year": data.year,
        "avg_temp": weather["avg_temp"],
        "total_rain": weather["total_rain"],
        "avg_wind": weather["avg_wind"]
    }

    # initialize all features as 0
    for col in feature_cols:
        row[col] = 0

    # set state feature
    state_col = f"state_{data.location}"
    if state_col in row:
        row[state_col] = 1

    # set crop feature
    crop_col = f"crop_{data.crop}"
    if crop_col in row:
        row[crop_col] = 1

    features = pd.DataFrame([row])[feature_cols]

    prediction = model.predict(features)[0]

    return {"predicted_yield": float(prediction)}