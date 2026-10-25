from fastapi import APIRouter, HTTPException

from app.domain.recommendations import recommend_activities
from app.providers.errors import ProviderError
from app.providers.open_meteo import OpenMeteoClient
from app.schemas.weather import WeatherReport, WeatherRequest

router = APIRouter()


@router.post("", response_model=WeatherReport)
async def get_weather(request: WeatherRequest) -> WeatherReport:
    try:
        forecast = await OpenMeteoClient().get_forecast(
            request.latitude,
            request.longitude,
            request.location_name,
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail="Weather provider is unavailable") from exc
    return forecast.model_copy(
        update={"recommendations": recommend_activities(forecast.current, request.language)}
    )
