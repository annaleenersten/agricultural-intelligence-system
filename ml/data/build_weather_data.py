# state
# county
# year

# avg_temp
# avg_temp_min
# max_temp
# total_rain
# rain_days
# heat_days
# avg_wind

# historical_avg_temp
# historical_avg_rain

# temp_difference
# rain_difference

import pandas as pd
import joblib
import os
import time

from backend.app.services.weather_service import get_weather_data
from ml.data.locationsAndCrops_config import COUNTY_COORDS


# -----------------------------
# FILES
# -----------------------------

YIELD_FILE = "ml/data/processed/yield_data.csv"

OUTPUT_FILE = "ml/data/processed/weather_data.csv"

CACHE_FILE = "ml/data/weather_cache.pkl"



# -----------------------------
# CACHE
# -----------------------------

def load_cache():

    if os.path.exists(CACHE_FILE):
        print("Loading weather cache...")
        return joblib.load(CACHE_FILE)

    return {}



def save_cache(cache):

    joblib.dump(
        cache,
        CACHE_FILE
    )



# -----------------------------
# WEATHER REQUEST
# -----------------------------

def get_year_weather(
        lat,
        lon,
        year,
        cache
):

    key = (
        lat,
        lon,
        year
    )


    if key in cache:

        return cache[key]


    weather = get_weather_data(
        lat,
        lon,
        f"{year}-04-01",
        f"{year}-09-30"
    )


    if weather:

        cache[key] = weather


    return weather



# -----------------------------
# BUILD DATASET
# -----------------------------

def build_weather_data():


    yield_df = pd.read_csv(
        YIELD_FILE
    )


    yield_df["state"] = (
        yield_df["state"]
        .str.upper()
        .str.strip()
    )


    yield_df["county"] = (
        yield_df["county"]
        .str.upper()
        .str.strip()
    )


    unique_locations = (
        yield_df[
            [
                "state",
                "county",
                "year"
            ]
        ]
        .drop_duplicates()
    )


    print(
        "Weather requests:",
        len(unique_locations)
    )


    cache = load_cache()


    rows = []


    for _, row in unique_locations.iterrows():


        state = row["state"]

        county = row["county"]

        year = int(row["year"])



        key = (
            state,
            county
        )


        if key not in COUNTY_COORDS:

            print(
                "Missing coordinates:",
                key
            )

            continue



        lat, lon = COUNTY_COORDS[key]


        print(
            f"Weather: {state} {county} {year}"
        )


        try:

            weather = get_year_weather(
                lat,
                lon,
                year,
                cache
            )


            if weather is None:

                continue



            rows.append({

                "state": state,

                "county": county,

                "year": year,


                "avg_temp":
                    weather["avg_temp"],


                "avg_temp_min":
                    weather["avg_temp_min"],


                "max_temp":
                    weather["max_temp"],


                "total_rain":
                    weather["total_rain"],


                "rain_days":
                    weather["rain_days"],


                "heat_days":
                    weather["heat_days"],


                "avg_wind":
                    weather["avg_wind"]

            })


        except Exception as e:

            print(
                "Weather error:",
                e
            )


        time.sleep(0.1)



        if len(rows) % 100 == 0:

            save_cache(cache)

            print(
                "Saved cache"
            )



    weather_df = pd.DataFrame(rows)



    if weather_df.empty:

        print(
            "No weather data created"
        )

        return



    # -----------------------------
    # HISTORICAL NORMALS
    # -----------------------------

    weather_df["historical_avg_temp"] = (

        weather_df
        .groupby(
            [
                "state",
                "county"
            ]
        )["avg_temp"]
        .transform("mean")

    )


    weather_df["historical_avg_rain"] = (

        weather_df
        .groupby(
            [
                "state",
                "county"
            ]
        )["total_rain"]
        .transform("mean")

    )



    # -----------------------------
    # WEATHER ANOMALIES
    # -----------------------------

    weather_df["temp_difference"] = (

        weather_df["avg_temp"]

        -

        weather_df["historical_avg_temp"]

    )



    weather_df["rain_difference"] = (

        weather_df["total_rain"]

        -

        weather_df["historical_avg_rain"]

    )



    os.makedirs(
        "ml/data/processed",
        exist_ok=True
    )


    weather_df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    save_cache(cache)


    print()
    print(
        "Weather dataset complete"
    )

    print(
        "Rows:",
        len(weather_df)
    )



if __name__ == "__main__":

    build_weather_data()