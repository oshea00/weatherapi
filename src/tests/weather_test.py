import pytest

from app import weather


class _FakeResponse:
    def __init__(self, payload: list[dict[str, str]]):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> list[dict[str, str]]:
        return self._payload


@pytest.mark.parametrize(
    "city,state,country,expected_params,expected_coordinates",
    [
        (
            "Seattle",
            None,
            None,
            {"city": "Seattle", "format": "json"},
            ("47.6038321", "-122.3300620"),
        ),
        (
            "Paris",
            None,
            None,
            {"city": "Paris", "format": "json"},
            ("48.8588897", "2.3200410"),
        ),
        (
            "Paris",
            None,
            "France",
            {"city": "Paris", "country": "France", "format": "json"},
            ("48.8588897", "2.3200410"),
        ),
        (
            "Paris",
            "TX",
            None,
            {"city": "Paris", "state": "TX", "format": "json"},
            ("33.6617962", "-95.5555130"),
        ),
        (
            "Paris",
            "Texas",
            None,
            {"city": "Paris", "state": "Texas", "format": "json"},
            ("33.6617962", "-95.5555130"),
        ),
    ],
)
def test_search_queries(
    monkeypatch: pytest.MonkeyPatch,
    city: str,
    state: str | None,
    country: str | None,
    expected_params: dict[str, str],
    expected_coordinates: tuple[str, str],
) -> None:
    def fake_get(url: str, params: dict[str, str]) -> _FakeResponse:
        assert url == f"{weather.BASE_MAP_URL}/search"
        assert params == expected_params
        lat, lon = expected_coordinates
        return _FakeResponse([{"lat": lat, "lon": lon}])

    monkeypatch.setattr(weather.GEOCODING_CLIENT, "get", fake_get)

    assert weather.get_coordinates(city=city, state=state, country=country) == expected_coordinates
