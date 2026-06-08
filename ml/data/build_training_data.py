from backend.app.services.crop_service import get_crop_yield_data
from backend.app.services.weather_service import get_weather_data
from backend.app.config.locationsAndCrops_config import (
    STATE_COORDS,
    STATES,
    CROPS
)

import pandas as pd
import joblib
import os
import time

START_YEAR = 2000
END_YEAR = 2023

CACHE_FILE = "ml/data/weather_cache.pkl"


def build_training_data():

    rows = []

    # -----------------------------
    # LOAD WEATHER CACHE
    # -----------------------------
    if os.path.exists(CACHE_FILE):
        weather_cache = joblib.load(CACHE_FILE)
        print(f"Loaded {len(weather_cache)} cached weather records")
    else:
        weather_cache = {}

    # -----------------------------
    # BUILD DATASET
    # -----------------------------
    for crop in CROPS:
        for state in STATES:

            print(f"\nProcessing {crop} - {state}")

            usda = get_crop_yield_data(
                crop,
                state,
                str(START_YEAR)
            )

            if usda is None or isinstance(usda, dict):
                print("Skipping USDA failure")
                continue

            lat, lon = STATE_COORDS[state]

            for _, r in usda.iterrows():

                year = int(r["year"])

                if year < START_YEAR or year > END_YEAR:
                    continue

                cache_key = (state, year)

                # -----------------------------
                # WEATHER CACHE
                # -----------------------------
                if cache_key not in weather_cache:

                    print(f"Fetching weather: {state} {year}")

                    weather = get_weather_data(
                        lat,
                        lon,
                        f"{year}-04-01",
                        f"{year}-09-30"
                    )

                    if weather is None:
                        print(f"Weather failed: {state} {year}")
                        continue

                    weather_cache[cache_key] = weather

                    # save cache immediately
                    joblib.dump(
                        weather_cache,
                        CACHE_FILE
                    )

                    # let API load
                    time.sleep(0.5)

                weather = weather_cache[cache_key]

                rows.append({
                    "year": year,
                    "state": state,
                    "crop": crop,

                    "yield": r["yield"],

                    "avg_temp": weather["avg_temp"],
                    "avg_temp_min": weather["avg_temp_min"],
                    "total_rain": weather["total_rain"],
                    "avg_wind": weather["avg_wind"],
                })

    # -----------------------------
    # CREATE DATAFRAME
    # -----------------------------
    df = pd.DataFrame(rows)

    if df.empty:
        print("No training data generated")
        return None

    df = df.dropna()

    # -----------------------------
    # ONE-HOT ENCODE
    # -----------------------------
    df = pd.get_dummies(
        df,
        columns=["state", "crop"]
    )

    # -----------------------------
    # SAVE FEATURE LIST
    # -----------------------------
    feature_cols = [
        c for c in df.columns
        if c != "yield"
    ]

    joblib.dump(
        feature_cols,
        "ml/models/features.pkl"
    )

    # -----------------------------
    # SAVE DATASET
    # -----------------------------
    df.to_csv(
        "ml/data/training_data.csv",
        index=False
    )

    print("\nTraining data saved")
    print(f"Rows: {len(df)}")
    print(f"Features: {len(feature_cols)}")

    return df


if __name__ == "__main__":
    build_training_data()