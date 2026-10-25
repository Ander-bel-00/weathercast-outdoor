from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.domain.recommendations import recommend_activities
from app.providers.errors import ProviderError
from app.providers.open_meteo import OpenMeteoClient
from app.schemas.weather import WeatherReport, WeatherRequest

router = APIRouter()


def get_weather_client() -> OpenMeteoClient:
    return OpenMeteoClient()


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
