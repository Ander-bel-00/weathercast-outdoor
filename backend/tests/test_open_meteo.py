import asyncio
from datetime import date

import httpx
import pytest

from app.providers.errors import ProviderError
from app.providers.open_meteo import OpenMeteoClient


def weather_payload() -> dict[str, object]:
    return {
        "latitude": 4.84,
        "longitude": -75.67,
        "timezone": "America/Bogota",
        "current": {
            "time": "2026-10-25T12:00",
            "temperature_2m": 22,
            "relative_humidity_2m": 60,
            "apparent_temperature": 21,
            "precipitation": 0.2,
            "weather_code": 2,
            "wind_speed_10m": 8,
        },
        "hourly": {
            "time": ["2026-10-25T12:00", "2026-10-25T13:00"],
            "temperature_2m": [22, 23],
            "precipitation_probability": [20, 35],
            "wind_speed_10m": [8, 10],
        },
        "daily": {
            "time": ["2026-10-25", "2026-10-26"],
            "weather_code": [2, 61],
            "temperature_2m_max": [26, 23],
            "temperature_2m_min": [16, 15],
            "precipitation_probability_max": [35, 80],
            "precipitation_sum": [0.3, 4.2],
            "wind_speed_10m_max": [12, 18],
        },
    }


def test_forecast_maps_hourly_and_daily_provider_fields() -> None:
    async def scenario() -> tuple[object, dict[str, object]]:
        request_params: dict[str, object] = {}

        def respond(request: httpx.Request) -> httpx.Response:
            request_params.update(dict(request.url.params))
            return httpx.Response(200, json=weather_payload())

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            report = await OpenMeteoClient(client).get_forecast(4.84, -75.67, "Dosquebradas")
        return report, request_params

    report, params = asyncio.run(scenario())

    assert params["forecast_days"] == "7"
    assert len(report.daily) == 2
    assert report.daily[1].date == date(2026, 10, 26)
    assert report.daily[1].temperature_max_c == 23
    assert report.daily[1].precipitation_probability_max_pct == 80
    assert report.hourly[1].temperature_c == 23


def test_city_search_maps_geocoding_results() -> None:
    async def scenario() -> tuple[list[object], list[httpx.Request]]:
        requests: list[httpx.Request] = []

        def respond(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "id": 3687238,
                            "name": "Dosquebradas",
                            "country": "Colombia",
                            "admin1": "Risaralda",
                            "latitude": 4.84,
                            "longitude": -75.67,
                            "timezone": "America/Bogota",
                        }
                    ]
                },
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            locations = await OpenMeteoClient(client).search_locations("Dosquebradas", "es")
        return locations, requests

    locations, requests = asyncio.run(scenario())

    assert len(locations) == 1
    assert locations[0].name == "Dosquebradas"
    assert locations[0].admin1 == "Risaralda"
    assert requests[0].url.params["language"] == "es"


def test_map_points_batch_locations_and_choose_nearest_precipitation_hour() -> None:
    requested: list[httpx.Request] = []

    def point_payload(latitude: float, longitude: float, temperature: int) -> dict[str, object]:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "current": {
                "time": "2026-10-25T12:00",
                "temperature_2m": temperature,
                "precipitation": 0.1,
                "weather_code": 2,
                "wind_speed_10m": 9,
            },
            "hourly": {
                "time": ["2026-10-25T11:00", "2026-10-25T12:00", "2026-10-25T13:00"],
                "precipitation_probability": [10, 35, 70],
            },
        }

    def respond(request: httpx.Request) -> httpx.Response:
        requested.append(request)
        return httpx.Response(
            200,
            json=[point_payload(4.8, -75.7, 22), point_payload(4.9, -75.6, 24)],
        )

    async def scenario() -> list[object]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await OpenMeteoClient(client).get_map_points([(4.8, -75.7), (4.9, -75.6)])

    points = asyncio.run(scenario())

    assert len(requested) == 1
    assert requested[0].url.params["latitude"] == "4.80000,4.90000"
    assert requested[0].url.params["current"] == (
        "temperature_2m,precipitation,weather_code,wind_speed_10m"
    )
    assert points[0].temperature_c == 22
    assert points[0].precipitation_probability_pct == 35
    assert points[1].longitude == -75.6


def test_city_search_provider_failure_is_wrapped() -> None:
    async def scenario() -> None:
        def respond(_: httpx.Request) -> httpx.Response:
            return httpx.Response(503)

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            await OpenMeteoClient(client).search_locations("Medellín", "es")

    with pytest.raises(ProviderError):
        asyncio.run(scenario())


def test_missing_daily_data_is_reported_as_provider_error() -> None:
    payload = weather_payload()
    del payload["daily"]

    async def scenario() -> None:
        async def respond(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=payload)

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            await OpenMeteoClient(client).get_forecast(4.84, -75.67, "Dosquebradas")

    with pytest.raises(ProviderError):
        asyncio.run(scenario())


def test_http_provider_failure_is_wrapped() -> None:
    async def scenario() -> None:
        async def respond(_: httpx.Request) -> httpx.Response:
            return httpx.Response(503)

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            await OpenMeteoClient(client).get_forecast(4.84, -75.67, "Dosquebradas")

    with pytest.raises(ProviderError):
        asyncio.run(scenario())
