from typing import Any, Optional
import httpx
from app.http_client import create_http_client

BASE_MAP_URL = "https://nominatim.openstreetmap.org"
BASE_WEATHER_URL = "https://api.weather.gov"
USER_AGENT = "MyLab.1.0 (contact: oshea00@gmail.com)"


class LocationNotFound(Exception):
    pass


GEOCODING_CLIENT = create_http_client(USER_AGENT)
WEATHER_CLIENT = create_http_client(USER_AGENT)


def get_coordinates(
    city: str,
    state: Optional[str] = None,
    country: Optional[str] = None,
) -> tuple[str, str]:
    query_params = {"city": city, "format": "json"}
    if state:
        query_params["state"] = state
    if country:
        query_params["country"] = country

    geocode_response = GEOCODING_CLIENT.get(
        f"{BASE_MAP_URL}/search",
        params=query_params,
    )
    geocode_response.raise_for_status()
    geocode_data = geocode_response.json()

    if not geocode_data:
        raise LocationNotFound(city)

    return (
        geocode_data[0]["lat"],
        geocode_data[0]["lon"],
    )


def get_forecast(lat: float, lon: float) -> Optional[list[dict[str, Any]]]:
    try:
        response = WEATHER_CLIENT.get(
            f"{BASE_WEATHER_URL}/points/{lat},{lon}",
        )
        response.raise_for_status()
        data = response.json()
        forecast_url = data["properties"]["forecast"]

        forecast_response = WEATHER_CLIENT.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        return forecast_data["properties"]["periods"]
    except httpx.HTTPStatusError:
        return None
