import asyncio
from datetime import UTC, date, datetime

import httpx

from app.api.routes.weather import get_weather_client
from app.main import app
from app.schemas.weather import (
    CurrentConditions,
    DailyForecast,
    HourlyPoint,
    WeatherReport,
)


class FakeWeatherClient:
    async def get_forecast(self, latitude: float, longitude: float, name: str) -> WeatherReport:
        return WeatherReport(
            location_name=name,
            latitude=latitude,
            longitude=longitude,
            timezone="America/Bogota",
            fetched_at=datetime.now(UTC),
            current=CurrentConditions(
                time=datetime(2026, 10, 25, 12),
                temperature_c=22,
                apparent_temperature_c=21,
                relative_humidity_pct=60,
                precipitation_mm=0,
                wind_speed_kmh=5,
                weather_code=1,
            ),
            hourly=[
                HourlyPoint(
                    time=datetime(2026, 10, 25, 12),
                    temperature_c=22,
                    precipitation_probability_pct=5,
                    wind_speed_kmh=5,
                )
            ],
            daily=[
                DailyForecast(
                    date=date(2026, 10, 25),
                    weather_code=1,
                    temperature_max_c=25,
                    temperature_min_c=15,
                    precipitation_probability_max_pct=10,
                    precipitation_sum_mm=0,
                    wind_speed_max_kmh=8,
                )
            ],
        )


def post_weather(payload: dict[str, object]) -> httpx.Response:
    async def scenario() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/api/v1/weather", json=payload)

    return asyncio.run(scenario())


def test_weather_route_returns_daily_forecast_and_default_recommendations() -> None:
    app.dependency_overrides[get_weather_client] = FakeWeatherClient
    try:
        response = post_weather(
            {"latitude": 4.84, "longitude": -75.67, "location_name": "Dosquebradas"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["daily"][0]["temperature_max_c"] == 25
    assert [item["activity"] for item in body["recommendations"]] == ["walk", "run", "bike"]


def test_weather_route_explains_forecast_rain_in_the_selected_language() -> None:
    class RainyWeatherClient(FakeWeatherClient):
        async def get_forecast(self, latitude: float, longitude: float, name: str) -> WeatherReport:
            report = await super().get_forecast(latitude, longitude, name)
            return report.model_copy(
                update={
                    "hourly": [
                        HourlyPoint(
                            time=datetime(2026, 10, 25, 12),
                            temperature_c=22,
                            precipitation_probability_pct=10,
                            wind_speed_kmh=5,
                        ),
                        HourlyPoint(
                            time=datetime(2026, 10, 25, 14),
                            temperature_c=21,
                            precipitation_probability_pct=85,
                            wind_speed_kmh=7,
                        ),
                    ]
                }
            )

    app.dependency_overrides[get_weather_client] = RainyWeatherClient
    try:
        response = post_weather(
            {
                "latitude": 4.84,
                "longitude": -75.67,
                "location_name": "Dosquebradas",
                "language": "es",
            }
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    walk = response.json()["recommendations"][0]
    assert walk["rating"] == "poor"
    assert "85% a las 14:00" in walk["reasons"][0]


def test_weather_route_rejects_invalid_coordinates_and_unknown_fields() -> None:
    app.dependency_overrides[get_weather_client] = FakeWeatherClient
    try:
        invalid_location = post_weather(
            {"latitude": 91, "longitude": 0, "location_name": "Nowhere"}
        )
        obsolete_preferences = post_weather(
            {
                "latitude": 0,
                "longitude": 0,
                "location_name": "Somewhere",
                "preferences": {
                    "walk": {"max_wind_speed_kmh": 35, "max_precipitation_mm": 2},
                },
            }
        )
    finally:
        app.dependency_overrides.clear()

    assert invalid_location.status_code == 422
    assert obsolete_preferences.status_code == 422
