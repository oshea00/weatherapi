import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from app.weather import LocationNotFound, get_coordinates, get_forecast

app = FastAPI(
    title="Weather API",
    summary="A thin gateway to US weather forecasts.",
    description=(
        "Geocodes a city via OpenStreetMap Nominatim, then returns the "
        "forecast periods from the National Weather Service "
        "(api.weather.gov). US locations only, since weather.gov covers "
        "only the United States."
    ),
    version="0.1.0",
    contact={"name": "Mike OShea", "email": "oshea00@gmail.com"},
)

# Comma-separated list of allowed origins; defaults to allowing any origin.
cors_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


class ProbabilityOfPrecipitation(BaseModel):
    unitCode: str
    value: Optional[int] = Field(
        default=None,
        description="Percent chance, or null when unavailable.",
    )


class ForecastPeriod(BaseModel):
    # Upstream may add fields; pass them through rather than dropping them.
    model_config = ConfigDict(extra="allow")

    number: int
    name: str = Field(description="Period label, e.g. 'Today' or 'Tonight'.")
    startTime: str = Field(description="ISO 8601 timestamp with UTC offset.")
    endTime: str = Field(description="ISO 8601 timestamp with UTC offset.")
    isDaytime: bool
    temperature: int
    temperatureUnit: str = Field(description="'F' or 'C'.")
    temperatureTrend: Optional[str] = None
    probabilityOfPrecipitation: Optional[ProbabilityOfPrecipitation] = None
    windSpeed: str = Field(description="Human-readable range, e.g. '1 to 6 mph'.")
    windDirection: str = Field(description="Compass abbreviation, e.g. 'NNW'.")
    icon: str
    shortForecast: str = Field(description="Brief summary, e.g. 'Sunny'.")
    detailedForecast: str


class WeatherResponse(BaseModel):
    weather: list[ForecastPeriod]


class ErrorDetail(BaseModel):
    detail: str


@app.get(
    "/weather",
    response_model=WeatherResponse,
    summary="Get the forecast for a city",
    tags=["weather"],
    responses={
        404: {
            "description": "Location not found, or no forecast available",
            "model": ErrorDetail,
        },
    },
)
def get_weather(
    city: str = Query(description="City name, e.g. 'Seattle'."),
    state: Optional[str] = Query(
        default=None,
        description="State name or abbreviation, e.g. 'WA'.",
    ),
    country: Optional[str] = Query(
        default="USA",
        description="Country; forecasts are only available for the USA.",
    ),
) -> WeatherResponse:

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
    return WeatherResponse(weather=forecast)
