import requests

def get_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "auto"
    }

    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()["daily"]

    return {
        "avg_temp": sum(data["temperature_2m_max"]) / len(data["temperature_2m_max"]),
        "avg_temp_min": sum(data["temperature_2m_min"]) / len(data["temperature_2m_min"]),
        "total_rain": sum(data["precipitation_sum"]),
        "avg_wind": sum(data["windspeed_10m_max"]) / len(data["windspeed_10m_max"]),
    }