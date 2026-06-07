from backend.app.services.crop_service import get_crop_yield_data
from backend.app.services.weather_service import get_weather_features
from backend.app.config.locationsAndCrops_config import STATE_COORDS
from backend.app.config.locationsAndCrops_config import STATES, CROPS
import pandas as pd
import joblib
import time

START_YEAR = 2000
END_YEAR = 2023


def build_training_data():

    rows = []

    for crop in CROPS:
        for state in STATES:

            usda = get_crop_yield_data(crop, state, str(START_YEAR))

            if usda is None or isinstance(usda, dict):
                continue

            lat, lon = STATE_COORDS[state]

            for _, r in usda.iterrows():

                year = int(r["year"])

                if year < START_YEAR or year > END_YEAR:
                    continue

                weather = get_weather_features(
                    lat,
                    lon,
                    f"{year}-04-01",
                    f"{year}-09-30"
                )

                if weather is None:
                    continue

                rows.append({
                    "year": year,
                    "state": state,
                    "crop": crop,
                    "yield": r["yield"],
                    "avg_temp": weather["avg_temp"],
                    "total_rain": weather["total_rain"],
                    "avg_wind": weather["avg_wind"],
                })

                time.sleep(0.2)

    df = pd.DataFrame(rows).dropna()

    # ONE HOT ENCODING
    df = pd.get_dummies(df, columns=["state", "crop"])

    # SAVE FEATURE COLUMNS (CRITICAL FIX)
    feature_cols = [c for c in df.columns if c != "yield"]
    joblib.dump(feature_cols, "ml/models/features.pkl")

    df.to_csv("ml/data/training_data.csv", index=False)

    print("Training data saved")
    return df


if __name__ == "__main__":
    build_training_data()