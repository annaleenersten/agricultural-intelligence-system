import pandas as pd
import joblib
import os
import time

from backend.app.services.weather_service import get_weather_data
from ml.data.locationsAndCrops_config import COUNTY_COORDS

# -----------------------------
# CONFIG
# -----------------------------
YIELD_FILE = "ml/data/yield_data.csv"
OUTPUT_FILE = "ml/data/weather_data.csv"
CACHE_FILE = "ml/data/weather_cache.pkl"


# -----------------------------
# CACHE
# -----------------------------
def load_cache():
    if os.path.exists(CACHE_FILE):
        print("Loading cache...")
        return joblib.load(CACHE_FILE)
    return {}


def save_cache(cache):
    joblib.dump(cache, CACHE_FILE)


# -----------------------------
# WEATHER FETCH (SAFE)
# -----------------------------
def safe_weather(lat, lon, year, cache):

    key = (lat, lon, year)

    if key in cache:
        return cache[key]

    try:
        weather = get_weather_data(
            lat,
            lon,
            f"{year}-04-01",
            f"{year}-09-30"
        )

        if weather:
            cache[key] = weather
            return weather

    except Exception as e:
        print(f"Weather error {key}: {e}")

    return None


# -----------------------------
# BUILD WEATHER DATASET
# -----------------------------
def build_weather_data():

    df_yield = pd.read_csv(YIELD_FILE)

    cache = load_cache()
    rows = []

    # 🚀 CRITICAL FIX: deduplicate first
    unique = df_yield[["state", "county", "year"]].drop_duplicates()

    print(f"Unique weather requests: {len(unique)}")

    for _, r in unique.iterrows():

        state = r["state"].upper()
        county = str(r["county"]).upper().strip()
        year = int(r["year"])

        key = (state, county)

        print(f"Processing {state} - {county} - {year}")

        if key not in COUNTY_COORDS:
            continue

        lat, lon = COUNTY_COORDS[key]

        weather = safe_weather(lat, lon, year, cache)

        if not weather:
            continue

        rows.append({
            "state": state,
            "county": county,
            "year": year,
            "avg_temp": weather["avg_temp"],
            "avg_temp_min": weather.get("avg_temp_min", weather["avg_temp"]),
            "total_rain": weather["total_rain"],
            "avg_wind": weather["avg_wind"],
        })

        # light throttle for API safety
        time.sleep(0.1)

        # periodic cache save
        if len(rows) % 100 == 0:
            save_cache(cache)
            print(f"Saved progress: {len(rows)} rows")

    # -----------------------------
    # SAVE OUTPUT
    # -----------------------------
    out = pd.DataFrame(rows)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    out.to_csv(OUTPUT_FILE, index=False)

    save_cache(cache)

    print("\nDONE")
    print(f"Weather rows: {len(out)}")

    return out


if __name__ == "__main__":
    build_weather_data()