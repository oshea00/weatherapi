# test functions in main.py
from fastapi.testclient import TestClient

from app.main import get_weather, app

client = TestClient(app)


def test_get_weather():
    response = client.get("/weather/London")
    assert response.status_code == 200
    assert response.json() == {
        "weather": "Weather in London"
    }
