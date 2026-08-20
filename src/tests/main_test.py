from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app

client = TestClient(app)


def sample_period(temperature=55):
    return {
        "number": 1,
        "name": "Today",
        "startTime": "2026-08-20T06:00:00-07:00",
        "endTime": "2026-08-20T18:00:00-07:00",
        "isDaytime": True,
        "temperature": temperature,
        "temperatureUnit": "F",
        "temperatureTrend": None,
        "probabilityOfPrecipitation": {
            "unitCode": "wmoUnit:percent",
            "value": 0,
        },
        "windSpeed": "1 to 6 mph",
        "windDirection": "NNW",
        "icon": "https://api.weather.gov/icons/land/day/few?size=medium",
        "shortForecast": "Sunny",
        "detailedForecast": "Sunny, with a high near 80.",
    }


def test_get_weather(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "get_coordinates",
        lambda city, state=None, country=None: ("47.6", "-122.3"),
    )
    monkeypatch.setattr(
        main_module,
        "get_forecast",
        lambda lat, lon: [sample_period()],
    )

    response = client.get("/weather?city=Seattle")
    assert response.status_code == 200
    assert response.json() == {"weather": [sample_period()]}


def test_get_weather_city_required():
    response = client.get("/weather")
    assert response.status_code == 422


def test_get_weather_city_state(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "get_coordinates",
        lambda city, state=None, country=None: ("47.6", "-122.3"),
    )
    monkeypatch.setattr(
        main_module,
        "get_forecast",
        lambda lat, lon: [sample_period()],
    )

    response = client.get("/weather?city=Seattle&state=wa")
    assert response.status_code == 200


def test_get_weather_city_state_country(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "get_coordinates",
        lambda city, state=None, country=None: ("33.6", "-95.5"),
    )
    monkeypatch.setattr(
        main_module,
        "get_forecast",
        lambda lat, lon: [sample_period(temperature=72)],
    )

    response = client.get("/weather?city=Paris&state=TX&country=USA")
    assert response.status_code == 200


def test_get_weather_badcity(monkeypatch):
    def _raise_city_not_found(city, state=None, country=None):
        raise main_module.LocationNotFound(city)

    monkeypatch.setattr(main_module, "get_coordinates", _raise_city_not_found)

    response = client.get("/weather?city=Wzzzbad")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Location not found"
    }


def test_get_weather_no_forecast(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "get_coordinates",
        lambda city, state=None, country=None: ("48.8", "2.3"),
    )
    monkeypatch.setattr(main_module, "get_forecast", lambda lat, lon: None)

    response = client.get("/weather?city=Paris&country=France")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Forecast not found"
    }
