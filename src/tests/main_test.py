# test functions in main.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_weather():
    response = client.get("/weather/Seattle")
    assert response.status_code == 200
    assert "weather" in response.json()
