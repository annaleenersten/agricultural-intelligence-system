import requests
import pandas as pd

def get_weather_data(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        # catches HTTP errors
        response.raise_for_status()

        data = response.json()

        if "daily" not in data:
            print("Weather API returned:", data)
            return None

        df = pd.DataFrame(data["daily"])

        return {
            "avg_temp": df["temperature_2m_max"].mean(),
            "avg_temp_min": df["temperature_2m_min"].mean(),
            "total_rain": df["precipitation_sum"].sum(),
            "avg_wind": df["windspeed_10m_max"].mean()
        }

    except requests.exceptions.RequestException as e:
        print("Weather API failed:", e)
        return None
