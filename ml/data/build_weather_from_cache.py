import joblib
import pandas as pd
import os

CACHE_FILE = "ml/data/weather_cache.pkl"
OUTPUT_FILE = "ml/data/weather_data.csv"


def build_weather_dataset():
    if not os.path.exists(CACHE_FILE):
        raise FileNotFoundError("No weather cache found")

    cache = joblib.load(CACHE_FILE)

    print("Loaded cache entries:", len(cache))

    rows = []

    for key, weather in cache.items():

        # skip bad entries
        if not weather or "avg_temp" not in weather:
            continue

        # -----------------------------
        # HANDLE MULTIPLE KEY TYPES
        # -----------------------------
        state = None
        county = None
        year = None

        if isinstance(key, tuple):

            if len(key) == 3:
                # (state, county, year)
                state, county, year = key

            elif len(key) == 2:
                # could be (lat, lon) OR (state, county)
                a, b = key

                # detect which one it is
                if isinstance(a, str) and isinstance(b, str):
                    state, county = a, b
                    year = 0  # fallback
                else:
                    continue

            else:
                continue

        else:
            continue

        # final safety check
        if state is None or county is None:
            continue

        rows.append({
            "state": str(state).upper().strip(),
            "county": str(county).upper().strip(),
            "year": int(year) if year else 0,

            "avg_temp": weather.get("avg_temp"),
            "avg_temp_min": weather.get("avg_temp_min", weather.get("avg_temp")),
            "total_rain": weather.get("total_rain"),
            "avg_wind": weather.get("avg_wind"),
        })

    df = pd.DataFrame(rows)

    if df.empty:
        print("No valid weather rows generated")
        return

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nDONE")
    print("Rows:", len(df))
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    build_weather_dataset()