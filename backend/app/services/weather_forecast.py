import requests
import pandas as pd


FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


def get_weather_forecast(lat, lon):

    params = {

        "latitude": lat,
        "longitude": lon,

        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),

        "forecast_days": 16,

        "timezone": "auto"
    }


    response = requests.get(
        FORECAST_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()


    data = response.json()


    daily = data["daily"]


    df = pd.DataFrame(daily)


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
            (
                df["precipitation_sum"] > 0
            ).sum(),


        "heat_days":
            (
                df["temperature_2m_max"] > 35
            ).sum(),


        "avg_wind":
            df["wind_speed_10m_max"].mean()
    }