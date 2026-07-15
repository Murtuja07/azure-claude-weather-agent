from typing import Any

import httpx

from app.config import get_settings


AZURE_MAPS_GEOCODING_URL = (
    "https://atlas.microsoft.com/geocode"
)


class LocationNotFoundError(ValueError):
    """Raised when Azure Maps cannot resolve a location."""


async def geocode_location(location: str) -> dict[str, Any]:
    """
    Convert a city, postcode or address into latitude and longitude.
    """
    settings = get_settings()

    if not location or not location.strip():
        raise ValueError("Location cannot be empty.")

    params = {
        "api-version": "2026-01-01",
        "query": location.strip(),
        "top": 1,
        "subscription-key": settings.azure_maps_subscription_key,
    }

    timeout = httpx.Timeout(10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(
            AZURE_MAPS_GEOCODING_URL,
            params=params,
        )
        response.raise_for_status()

    payload = response.json()
    features = payload.get("features", [])

    if not features:
        raise LocationNotFoundError(
            f"Location could not be found: {location}"
        )

    feature = features[0]

    geometry = feature.get("geometry", {})
    coordinates = geometry.get("coordinates", [])

    if len(coordinates) < 2:
        raise LocationNotFoundError(
            f"Coordinates were not returned for: {location}"
        )

    longitude = coordinates[0]
    latitude = coordinates[1]

    properties = feature.get("properties", {})

    return {
        "query": location,
        "resolved_name": (
            properties.get("address", {}).get("formattedAddress")
            or properties.get("name")
            or location
        ),
        "latitude": latitude,
        "longitude": longitude,
    }