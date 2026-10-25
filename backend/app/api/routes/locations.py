from fastapi import APIRouter, HTTPException, Query

from app.providers.open_meteo import OpenMeteoClient, ProviderError
from app.schemas.location import Location

router = APIRouter()


@router.get("/search", response_model=list[Location])
async def search_locations(q: str = Query(min_length=2, max_length=100)) -> list[Location]:
    try:
        return await OpenMeteoClient().search_locations(q)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail="Weather provider is unavailable") from exc
