from fastapi import APIRouter

from app.api.routes.locations import router as locations_router
from app.api.routes.weather import router as weather_router

api_router = APIRouter()
api_router.include_router(locations_router, prefix="/locations", tags=["locations"])
api_router.include_router(weather_router, prefix="/weather", tags=["weather"])
