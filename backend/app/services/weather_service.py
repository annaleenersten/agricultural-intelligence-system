import requests
import pandas as pd
import time
import random


# -----------------------------
# SAFE REQUEST WITH BACKOFF
# -----------------------------
def safe_weather_request(url, params, retries=5, timeout=60):

    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r

        except Exception as e:
            wait = (2 ** i) + random.uniform(0, 1)
            print(f"Weather retry {i+1}/{retries} failed: {e} | waiting {wait:.1f}s")
            time.sleep(wait)

    return None


# -----------------------------
# MAIN WEATHER FUNCTION
# -----------------------------
def get_weather_data(lat, lon, start_date, end_date):

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "windspeed_10m_max"
        ),
        "timezone": "auto"
    }

    response = safe_weather_request(url, params)

    if response is None:
        return None

    try:
        data = response.json()
    except Exception:
        return None

    # -----------------------------
    # VALIDATION
    # -----------------------------
    if "daily" not in data or data["daily"] is None:
        print("Bad API response:", data)
        return None

    daily = data["daily"]

    required = [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "windspeed_10m_max"
    ]

    if any(k not in daily for k in required):
        print("Missing weather keys")
        return None

    df = pd.DataFrame(daily)

    if df.empty:
        return None

    df = df.dropna()

    if df.empty:
        return None

    return {
        "avg_temp": df["temperature_2m_max"].mean(),
        "avg_temp_min": df["temperature_2m_min"].mean(),
        "total_rain": df["precipitation_sum"].sum(),
        "avg_wind": df["windspeed_10m_max"].mean()
    }
