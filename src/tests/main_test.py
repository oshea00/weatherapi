# test functions in main.py
import pytest

from app.main import get_weather


def test_get_weather():
    assert get_weather("London") == "Weather in London"
