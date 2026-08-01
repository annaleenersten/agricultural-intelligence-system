from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.services.weather_forecast import get_weather_forecast
from backend.app.services.price_service import get_crop_price
from backend.app.services.profit_service import calculate_profit

from pydantic import BaseModel

import pandas as pd
import joblib
import os

from datetime import datetime


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def clean_json(data):

    import numpy as np
    import pandas as pd

    if isinstance(data, dict):
        return {
            key: clean_json(value)
            for key, value in data.items()
        }

    elif isinstance(data, list):
        return [
            clean_json(item)
            for item in data
        ]

    elif isinstance(data, pd.Series):
        return clean_json(data.to_dict())

    elif isinstance(data, pd.DataFrame):
        return clean_json(data.to_dict(orient="records"))

    elif isinstance(data, (np.integer, np.floating)):
        return data.item()

    else:
        return data


# --------------------------------------------------
# LOAD MODEL ARTIFACTS
# --------------------------------------------------

MODEL_PATH = "ml/models/crop_model.pkl"
FEATURE_PATH = "ml/models/features.pkl"
COUNTY_PATH = "ml/models/county_coords.pkl"


model = joblib.load(MODEL_PATH)

feature_cols = joblib.load(
    FEATURE_PATH
)

COUNTY_COORDS = joblib.load(
    COUNTY_PATH
)


# --------------------------------------------------
# LOAD DATASETS
# --------------------------------------------------

WEATHER_FILE = (
    "ml/data/processed/weather_data.csv"
)

YIELD_FILE = (
    "ml/data/processed/yield_data.csv"
)


weather_df = pd.read_csv(
    WEATHER_FILE
)

yield_df = pd.read_csv(
    YIELD_FILE
)



# clean datasets

for df in [weather_df, yield_df]:

    df["state"] = (
        df["state"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df["county"] = (
        df["county"]
        .astype(str)
        .str.upper()
        .str.strip()
    )


yield_df["crop"] = (
    yield_df["crop"]
    .astype(str)
    .str.upper()
    .str.strip()
)



# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class YieldRequest(BaseModel):

    state: str
    county: str
    crop: str



# --------------------------------------------------
# PREDICT
# --------------------------------------------------

@app.post("/predict-yield")
def predict_yield(req: YieldRequest):


    state = req.state.upper()
    county = req.county.upper()
    crop = req.crop.upper()



    # -------------------------------
    # COUNTY LOCATION
    # -------------------------------

    key = (
        state,
        county
    )


    if key not in COUNTY_COORDS:

        raise HTTPException(
            status_code=400,
            detail="Invalid county"
        )


    lat, lon = COUNTY_COORDS[key]



    # -------------------------------
    # WEATHER FORECAST
    # -------------------------------

    weather = get_weather_forecast(
        lat,
        lon
    )


    if weather is None:

        raise HTTPException(
            status_code=500,
            detail="Weather unavailable"
        )



    # -------------------------------
    # HISTORICAL WEATHER
    # -------------------------------

    hist_weather = weather_df[
        (weather_df["state"] == state) &
        (weather_df["county"] == county)
    ]


    if hist_weather.empty:

        historical_avg_temp = 0
        historical_avg_rain = 0

    else:

        historical_avg_temp = (
            hist_weather["avg_temp"]
            .mean()
        )


        historical_avg_rain = (
            hist_weather["total_rain"]
            .mean()
        )



    temp_difference = (
        weather["avg_temp"]
        -
        historical_avg_temp
    )


    rain_difference = (
        weather["total_rain"]
        -
        historical_avg_rain
    )



    # -------------------------------
    # HISTORICAL YIELD
    # -------------------------------


    hist_yield = yield_df[
        (yield_df["state"] == state) &
        (yield_df["county"] == county) &
        (yield_df["crop"] == crop)
    ].sort_values(
        "year"
    )



    if hist_yield.empty:

        previous_year_yield = 0
        five_year_avg_yield = 0

    else:

        previous_year_yield = (
            hist_yield.iloc[-1]["yield"]
        )


        five_year_avg_yield = (
            hist_yield
            .tail(5)["yield"]
            .mean()
        )



    # -------------------------------
    # PRICE
    # -------------------------------

    price_df = get_crop_price(crop)


    if price_df.empty:

        price = 0

    else:

        latest_price = (
            price_df
            .sort_values("year")
            .iloc[-1]
        )

        price = float(
            latest_price["price"]
        )


    # -------------------------------
    # BUILD MODEL INPUT
    # -------------------------------


    row = {
        col: 0
        for col in feature_cols
    }



    row["year"] = (
        datetime.now().year
    )


    # weather

    row["avg_temp"] = weather["avg_temp"]

    row["avg_temp_min"] = weather["avg_temp_min"]

    row["max_temp"] = weather["max_temp"]

    row["total_rain"] = weather["total_rain"]

    row["rain_days"] = weather["rain_days"]

    row["heat_days"] = weather["heat_days"]

    row["avg_wind"] = weather["avg_wind"]



    # historical weather

    row["historical_avg_temp"] = (
        historical_avg_temp
    )

    row["historical_avg_rain"] = (
        historical_avg_rain
    )


    row["temp_difference"] = (
        temp_difference
    )


    row["rain_difference"] = (
        rain_difference
    )



    # historical yield

    row["previous_year_yield"] = (
        previous_year_yield
    )


    row["five_year_avg_yield"] = (
        five_year_avg_yield
    )



    # price

    row["price"] = price



    # categorical features

    for col, value in [
        ("state", state),
        ("county", county),
        ("crop", crop)
    ]:

        encoded = (
            f"{col}_{value}"
        )


        if encoded in row:

            row[encoded] = 1



    X = pd.DataFrame(
        [row]
    )[feature_cols]



    # -------------------------------
    # PREDICTION
    # -------------------------------

    prediction = model.predict(
        X
    )[0]


    profit = calculate_profit(
        crop,
        prediction
    )



    # -------------------------------
    # RESPONSE
    # -------------------------------


    response = {

    "location": {
        "state": state,
        "county": county,
        "crop": crop
    },


    "predicted_yield": float(prediction),


    "profit": profit,


    "weather": {

        "forecast": weather,

        "historical_average": {

            "temperature": historical_avg_temp,

            "rain": historical_avg_rain
        },

        "difference": {

            "temperature": temp_difference,

            "rain": rain_difference
        }
    },


    "historical_yield": {

        "previous_year": float(previous_year_yield),

        "five_year_average": float(five_year_avg_yield)
    }

    }

    return clean_json(response)





# --------------------------------------------------
# COUNTIES ENDPOINT
# --------------------------------------------------

@app.get("/counties/{state}")
def get_counties(state: str):

    state = state.upper()


    counties = sorted(
        {
            county
            for (
                s,
                county
            ) in COUNTY_COORDS.keys()

            if s == state
        }
    )


    return {
        "counties": counties
    }