from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

BASE_URL = "https://api.weather.gov"


@app.get("/weather/{city}")
def get_weather(city: str):
    if "," in city:
        city, state = city.split(",")
        geocode_url = f"https://nominatim.openstreetmap.org/search?city={city}&state={state}&format=json"
    else:
        geocode_url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
    geocode_response = httpx.get(geocode_url)
    geocode_response.raise_for_status()
    geocode_data = geocode_response.json()

    if not geocode_data:
        raise HTTPException(
            status_code=404, detail="City not found"
        )

    lat = geocode_data[0]["lat"]
    lon = geocode_data[0]["lon"]

    forecast = get_forecast(lat, lon)
    if forecast is None:
        raise HTTPException(
            status_code=404,
            detail="Forecast not found",
        )
    return {"weather": forecast}


def get_forecast(lat: float, lon: float) -> str:
    try:
        response = httpx.get(
            f"{BASE_URL}/points/{lat},{lon}",
            follow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()
        forecast_url = data["properties"]["forecast"]

        forecast_response = httpx.get(
            forecast_url, follow_redirects=True
        )
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        return forecast_data["properties"]["periods"][
            0
        ]["detailedForecast"]
    except httpx.HTTPStatusError:
        return None
