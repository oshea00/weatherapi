# test functions in main.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_weather():
    response = client.get("/weather/Seattle")
    assert response.status_code == 200
    assert "weather" in response.json()


def test_get_weather_city_state():
    response = client.get("/weather/Seattle,wa")
    assert response.status_code == 200


def test_get_weather_badcity():
    response = client.get("/weather/Wzzzbad")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "City not found"
    }


def test_get_weather_no_forecast():
    response = client.get("/weather/Paris")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Forecast not found"
    }
