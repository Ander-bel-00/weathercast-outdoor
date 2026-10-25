from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.domain.recommendations import recommend_activities
from app.providers.errors import ProviderError
from app.providers.open_meteo import OpenMeteoClient
from app.schemas.weather import WeatherMapPoint, WeatherReport, WeatherRequest

router = APIRouter()


def get_weather_client() -> OpenMeteoClient:
    return OpenMeteoClient()


def _longitude_in_range(longitude: float) -> float:
    return (longitude + 180) % 360 - 180


def _weather_grid(
    north: float, east: float, south: float, west: float
) -> list[tuple[float, float]]:
    if north <= south:
        raise HTTPException(status_code=422, detail="Map north bound must exceed south bound")
    longitude_span = (east - west) % 360
    if longitude_span == 0 and east != west:
        longitude_span = 360
    if north - south > 20 or longitude_span > 20:
        raise HTTPException(status_code=422, detail="Zoom in to load a local weather layer")

    fractions = (0.2, 0.5, 0.8)
    return [
        (
            south + (north - south) * latitude_fraction,
            _longitude_in_range(west + longitude_span * longitude_fraction),
        )
        for latitude_fraction in fractions
        for longitude_fraction in fractions
    ]


@router.get("/map-grid", response_model=list[WeatherMapPoint])
async def get_weather_map_grid(
    north: Annotated[float, Query(ge=-85.05, le=85.05)],
    east: Annotated[float, Query(ge=-540, le=540)],
    south: Annotated[float, Query(ge=-85.05, le=85.05)],
    west: Annotated[float, Query(ge=-540, le=540)],
    client: Annotated[OpenMeteoClient, Depends(get_weather_client)],
) -> list[WeatherMapPoint]:
    try:
        coordinates = _weather_grid(north, east, south, west)
        return await client.get_map_points(coordinates)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail="Weather provider is unavailable") from exc


@router.post("", response_model=WeatherReport)
async def get_weather(
    request: WeatherRequest,
    client: Annotated[OpenMeteoClient, Depends(get_weather_client)],
) -> WeatherReport:
    try:
        forecast = await client.get_forecast(
            request.latitude,
            request.longitude,
            request.location_name,
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail="Weather provider is unavailable") from exc
    return forecast.model_copy(
        update={
            "recommendations": recommend_activities(
                forecast.current, forecast.hourly, request.language
            )
        }
    )
