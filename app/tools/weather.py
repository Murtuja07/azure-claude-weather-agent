from typing import Any

import httpx

from app.config import get_settings
from app.tools.geocoding import geocode_location


AZURE_MAPS_CURRENT_WEATHER_URL = (
    "https://atlas.microsoft.com/weather/currentConditions/json"
)

AZURE_MAPS_DAILY_FORECAST_URL = (
    "https://atlas.microsoft.com/weather/forecast/daily/json"
)


def _value(metric: dict[str, Any] | None) -> Any:
    if not metric:
        return None
    return metric.get("value")


async def get_current_weather(
    location: str,
    units: str = "metric",
) -> dict[str, Any]:
    settings = get_settings()
    resolved_location = await geocode_location(location)

    unit_code = "metric" if units == "metric" else "imperial"

    params = {
        "api-version": "1.1",
        "query": (
            f"{resolved_location['latitude']},"
            f"{resolved_location['longitude']}"
        ),
        "unit": unit_code,
        "details": "true",
        "subscription-key": settings.azure_maps_subscription_key,
    }

    timeout = httpx.Timeout(10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(
            AZURE_MAPS_CURRENT_WEATHER_URL,
            params=params,
        )
        response.raise_for_status()

    payload = response.json()
    results = payload.get("results", [])

    if not results:
        raise ValueError(
            f"No current weather was returned for {location}."
        )

    current = results[0]

    return {
        "location": resolved_location["resolved_name"],
        "latitude": resolved_location["latitude"],
        "longitude": resolved_location["longitude"],
        "observation_time": current.get("dateTime"),
        "condition": current.get("phrase"),
        "temperature": _value(current.get("temperature")),
        "feels_like": _value(
            current.get("realFeelTemperature")
        ),
        "relative_humidity": current.get("relativeHumidity"),
        "wind_speed": _value(
            current.get("wind", {}).get("speed")
        ),
        "wind_direction": (
            current.get("wind", {})
            .get("direction", {})
            .get("localizedDescription")
        ),
        "visibility": _value(current.get("visibility")),
        "uv_index": current.get("uvIndex"),
        "has_precipitation": current.get("hasPrecipitation"),
        "precipitation_type": current.get("precipitationType"),
        "units": units,
    }


async def get_daily_forecast(
    location: str,
    days: int = 5,
    units: str = "metric",
) -> dict[str, Any]:
    settings = get_settings()
    resolved_location = await geocode_location(location)

    allowed_days = {1, 5, 10, 15, 25, 45}

    if days not in allowed_days:
        days = 5

    params = {
        "api-version": "1.1",
        "query": (
            f"{resolved_location['latitude']},"
            f"{resolved_location['longitude']}"
        ),
        "duration": days,
        "unit": units,
        "details": "true",
        "subscription-key": settings.azure_maps_subscription_key,
    }

    timeout = httpx.Timeout(10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(
            AZURE_MAPS_DAILY_FORECAST_URL,
            params=params,
        )
        response.raise_for_status()

    payload = response.json()
    forecasts = payload.get("forecasts", [])

    simplified_forecasts = []

    for forecast in forecasts:
        temperature = forecast.get("temperature", {})
        daytime = forecast.get("day", {})
        nighttime = forecast.get("night", {})

        simplified_forecasts.append(
            {
                "date": forecast.get("date"),
                "minimum_temperature": _value(
                    temperature.get("minimum")
                ),
                "maximum_temperature": _value(
                    temperature.get("maximum")
                ),
                "day_condition": daytime.get("phrase"),
                "night_condition": nighttime.get("phrase"),
                "day_rain_probability": (
                    daytime.get("rainProbability")
                ),
                "night_rain_probability": (
                    nighttime.get("rainProbability")
                ),
                "day_thunderstorm_probability": (
                    daytime.get("thunderstormProbability")
                ),
                "day_wind_speed": _value(
                    daytime.get("wind", {}).get("speed")
                ),
            }
        )

    return {
        "location": resolved_location["resolved_name"],
        "units": units,
        "forecast_count": len(simplified_forecasts),
        "forecasts": simplified_forecasts,
    }