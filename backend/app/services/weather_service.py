import requests
import pandas as pd
import time
import random


WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"


def safe_weather_request(params, retries=5):

    for attempt in range(retries):
        try:
            response = requests.get(
                WEATHER_URL,
                params=params,
                timeout=60
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            wait = (2 ** attempt) + random.random()
            print(
                f"Weather request failed "
                f"{attempt + 1}/{retries}: {e}"
            )

            time.sleep(wait)

    return None


def get_weather_data(lat, lon, start_date, end_date):

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),
        "timezone": "auto"
    }


    data = safe_weather_request(params)

    if not data or "daily" not in data:
        return None


    daily = data["daily"]

    df = pd.DataFrame(daily)

    if df.empty:
        return None


    df = df.dropna()


    if df.empty:
        return None


    return {

        "avg_temp":
            df["temperature_2m_max"].mean(),

        "avg_temp_min":
            df["temperature_2m_min"].mean(),


        "max_temp":
            df["temperature_2m_max"].max(),


        "total_rain":
            df["precipitation_sum"].sum(),


        "rain_days":
            (df["precipitation_sum"] > 0).sum(),


        "heat_days":
            (df["temperature_2m_max"] > 35).sum(),


        "avg_wind":
            df["wind_speed_10m_max"].mean()
    }
