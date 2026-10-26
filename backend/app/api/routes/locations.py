from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.providers.errors import ProviderError
from app.providers.nominatim import NominatimClient
from app.providers.open_meteo import OpenMeteoClient
from app.schemas.location import Location, ReverseLocationRequest

router = APIRouter()


@router.get("/search", response_model=list[Location])
async def search_locations(
    q: str = Query(min_length=2, max_length=100),
    language: Literal["en", "es"] = "en",
) -> list[Location]:
    try:
        return await OpenMeteoClient().search_locations(q, language)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail="Weather provider is unavailable") from exc


@router.post("/reverse", response_model=Location)
async def reverse_location(request: ReverseLocationRequest) -> Location:
    try:
        return await NominatimClient().reverse(
            request.latitude, request.longitude, request.language
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail="Nearby place lookup is unavailable") from exc
