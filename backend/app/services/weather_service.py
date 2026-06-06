import requests
import pandas as pd

def get_weather_features(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "past_days": 7,
        "forecast_days": 0,
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    print("API RESPONSE:", data)

    if "daily" not in data:
        return {
            "error": "No 'daily' key in response",
            "api_response": data
        }

    daily = data["daily"]

    df = pd.DataFrame(daily)

    print(df.columns)

    return {
        "avg_temp": df["temperature_2m_max"].mean(),
        "avg_temp_min": df["temperature_2m_min"].mean(),
        "total_rain": df["precipitation_sum"].sum(),
        "avg_wind": df["windspeed_10m_max"].mean()
    }