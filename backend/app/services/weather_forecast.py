import requests

def get_weather_forecast(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&daily=temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_sum,"
        "wind_speed_10m_max"
        "&forecast_days=16"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    daily = data["daily"]

    return {
        "avg_temp":
            sum(daily["temperature_2m_max"]) /
            len(daily["temperature_2m_max"]),

        "total_rain":
            sum(daily["precipitation_sum"]),

        "avg_wind":
            sum(daily["wind_speed_10m_max"]) /
            len(daily["wind_speed_10m_max"]),
    }