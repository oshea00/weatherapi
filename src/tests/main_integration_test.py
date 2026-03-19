import os
import time

import pytest
from fastapi.testclient import TestClient

from app import weather
from app.main import app

RUN_INTEGRATION_TESTS = os.getenv("RUN_INTEGRATION_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_INTEGRATION_TESTS,
    reason="Set RUN_INTEGRATION_TESTS=1 to run live API integration tests.",
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def pace_integration_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    last_request_at = {"time": 0.0}

    geocoding_get = weather.GEOCODING_CLIENT.get
    weather_get = weather.WEATHER_CLIENT.get

    def _paced_get(getter):
        def _wrapped(*args, **kwargs):
            wait_for = 2.0 - (time.monotonic() - last_request_at["time"])
            if wait_for > 0:
                time.sleep(wait_for)
            response = getter(*args, **kwargs)
            last_request_at["time"] = time.monotonic()
            return response

        return _wrapped

    monkeypatch.setattr(weather.GEOCODING_CLIENT, "get", _paced_get(geocoding_get))
    monkeypatch.setattr(weather.WEATHER_CLIENT, "get", _paced_get(weather_get))


def test_get_weather_integration() -> None:
    response = client.get("/weather?city=Seattle")
    assert response.status_code == 200
    assert "weather" in response.json()


def test_get_weather_city_state_integration() -> None:
    response = client.get("/weather?city=Seattle&state=wa")
    assert response.status_code == 200


def test_get_weather_city_state_country_integration() -> None:
    response = client.get("/weather?city=Paris&state=TX&country=USA")
    assert response.status_code == 200


def test_get_weather_badcity_integration() -> None:
    response = client.get("/weather?city=Wzzzbad")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "City not found"
    }


def test_get_weather_no_forecast_integration() -> None:
    response = client.get("/weather?city=Paris&country=France")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Forecast not found"
    }
