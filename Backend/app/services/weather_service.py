import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_data(latitude: float, longitude: float):
    """
    Fetch recent hourly rainfall/weather data for a zone.

    Uses Open-Meteo's public forecast API.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "rain,precipitation,temperature_2m,relative_humidity_2m",
        "past_hours": 24,
        "forecast_hours": 1,
        "timezone": "auto",
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


def get_last_24h_rainfall(
    latitude: float,
    longitude: float
):
    """
    Calculate total rainfall over the most recent 24 hourly observations.
    """

    data = get_weather_data(
        latitude=latitude,
        longitude=longitude
    )

    hourly = data.get("hourly", {})

    rain_values = hourly.get("rain", [])

    if not rain_values:
        raise ValueError(
            "No rainfall data returned by weather service"
        )

    # Remove None values
    valid_rain_values = [
        float(value)
        for value in rain_values
        if value is not None
    ]

    rainfall_24h = sum(valid_rain_values)

    return {
        "rainfall_24h": round(rainfall_24h, 2),
        "temperature": (
            hourly.get("temperature_2m", [None])[-1]
        ),
        "relative_humidity": (
            hourly.get("relative_humidity_2m", [None])[-1]
        ),
        "source": "Open-Meteo",
        "latitude": latitude,
        "longitude": longitude
    }