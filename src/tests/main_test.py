from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app

client = TestClient(app)


def test_get_weather(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "get_coordinates",
        lambda city, state=None, country=None: ("47.6", "-122.3"),
    )
    monkeypatch.setattr(
        main_module,
        "get_forecast",
        lambda lat, lon: [{"name": "Today", "temperature": 55}],
    )

    response = client.get("/weather?city=Seattle")
    assert response.status_code == 200
    assert "weather" in response.json()


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
        lambda lat, lon: [{"name": "Today", "temperature": 55}],
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
        lambda lat, lon: [{"name": "Today", "temperature": 72}],
    )

    response = client.get("/weather?city=Paris&state=TX&country=USA")
    assert response.status_code == 200


def test_get_weather_badcity(monkeypatch):
    def _raise_city_not_found(city, state=None, country=None):
        raise main_module.CityNotFoundError(city)

    monkeypatch.setattr(main_module, "get_coordinates", _raise_city_not_found)

    response = client.get("/weather?city=Wzzzbad")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "City not found"
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
