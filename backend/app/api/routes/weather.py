from fastapi import APIRouter, HTTPException, Query

from app.domain.recommendations import recommend_activities
from app.providers.open_meteo import OpenMeteoClient, ProviderError
from app.schemas.weather import WeatherReport

router = APIRouter()


@router.get("", response_model=WeatherReport)
async def get_weather(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    location_name: str = Query(min_length=1, max_length=100),
) -> WeatherReport:
    try:
        forecast = await OpenMeteoClient().get_forecast(latitude, longitude, location_name)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail="Weather provider is unavailable") from exc
    return forecast.model_copy(update={"recommendations": recommend_activities(forecast.current)})
