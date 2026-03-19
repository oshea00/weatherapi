from typing import Optional
from fastapi import FastAPI, HTTPException
from app.weather import LocationNotFound, get_coordinates, get_forecast

app = FastAPI()


@app.get("/weather")
def get_weather(
    city: str,
    state: Optional[str] = None,
    country: Optional[str] = "USA",
) -> dict:

    try:
        lat, lon = get_coordinates(city, state=state, country=country)
    except LocationNotFound:
        raise HTTPException(
            status_code=404,
            detail="Location not found",
        )

    forecast = get_forecast(lat, lon)
    if forecast is None:
        raise HTTPException(
            status_code=404,
            detail="Forecast not found",
        )
    return {"weather": forecast}
