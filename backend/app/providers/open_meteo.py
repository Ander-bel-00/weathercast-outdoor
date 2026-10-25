from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx

from app.schemas.location import Location
from app.schemas.weather import CurrentConditions, HourlyPoint, WeatherReport

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


class ProviderError(Exception):
    """Raised when the weather provider cannot return usable data."""


class OpenMeteoClient:
    """Translate Open-Meteo responses into provider-independent app schemas."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def search_locations(self, query: str) -> list[Location]:
        params = {"name": query, "count": 8, "language": "en", "format": "json"}
        try:
            async with self._client_scope() as client:
                response = await client.get(GEOCODING_URL, params=params)
                response.raise_for_status()
                rows = response.json().get("results", [])
                return [
                    Location(
                        id=row["id"],
                        name=row["name"],
                        country=row.get("country", ""),
                        admin1=row.get("admin1"),
                        latitude=row["latitude"],
                        longitude=row["longitude"],
                        timezone=row.get("timezone", "UTC"),
                    )
                    for row in rows
                ]
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise ProviderError from exc

    async def get_forecast(self, latitude: float, longitude: float, name: str) -> WeatherReport:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,precipitation_probability,wind_speed_10m",
            "forecast_days": 2,
            "timezone": "auto",
            "wind_speed_unit": "kmh",
        }
        try:
            async with self._client_scope() as client:
                response = await client.get(FORECAST_URL, params=params)
                response.raise_for_status()
                payload = response.json()
                current = payload["current"]
                hourly = payload["hourly"]
                current_conditions = CurrentConditions(
                    time=current["time"],
                    temperature_c=current["temperature_2m"],
                    apparent_temperature_c=current["apparent_temperature"],
                    relative_humidity_pct=current["relative_humidity_2m"],
                    precipitation_mm=current["precipitation"],
                    wind_speed_kmh=current["wind_speed_10m"],
                    weather_code=current["weather_code"],
                )
                hourly_points = [
                    HourlyPoint(
                        time=time,
                        temperature_c=hourly["temperature_2m"][index],
                        precipitation_probability_pct=hourly["precipitation_probability"][index],
                        wind_speed_kmh=hourly["wind_speed_10m"][index],
                    )
                    for index, time in enumerate(hourly["time"])
                ]
                return WeatherReport(
                    location_name=name,
                    latitude=payload["latitude"],
                    longitude=payload["longitude"],
                    timezone=payload["timezone"],
                    fetched_at=datetime.now(UTC),
                    current=current_conditions,
                    hourly=hourly_points,
                )
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError from exc

    @asynccontextmanager
    async def _client_scope(self) -> AsyncIterator[httpx.AsyncClient]:
        if self._client is not None:
            yield self._client
            return
        async with httpx.AsyncClient(timeout=8.0) as client:
            yield client
