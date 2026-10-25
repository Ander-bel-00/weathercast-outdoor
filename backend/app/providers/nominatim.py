import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import monotonic
from typing import Literal

import httpx

from app.providers.errors import ProviderError
from app.schemas.location import Location

NOMINATIM_URL = os.getenv(
    "WEATHERCAST_REVERSE_GEOCODER_URL",
    "https://nominatim.openstreetmap.org/reverse",
)
USER_AGENT = "WeatherCast/0.1 (https://github.com/Ander-bel-00/weathercast-outdoor)"
CACHE_TTL_SECONDS = 21_600
_cache: dict[tuple[float, float, str], tuple[float, Location]] = {}
_cache_lock = asyncio.Lock()
_last_request_at = 0.0


class NominatimClient:
    """Reverse geocode a user-requested location and cache low-volume lookups."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def reverse(
        self,
        latitude: float,
        longitude: float,
        language: Literal["en", "es"],
    ) -> Location:
        global _last_request_at

        cache_key = (round(latitude, 3), round(longitude, 3), language)
        async with _cache_lock:
            cached = _cache.get(cache_key)
            if cached and cached[0] > monotonic():
                return cached[1].model_copy(update={"latitude": latitude, "longitude": longitude})

            wait_seconds = 1.0 - (monotonic() - _last_request_at)
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "addressdetails": 1,
                "zoom": 10,
                "accept-language": language,
            }
            try:
                async with self._client_scope() as client:
                    _last_request_at = monotonic()
                    response = await client.get(NOMINATIM_URL, params=params)
                    response.raise_for_status()
                    payload = response.json()
            except (httpx.HTTPError, AttributeError, TypeError, ValueError) as exc:
                raise ProviderError from exc

            address = payload.get("address", {})
            name = next(
                (
                    address[key]
                    for key in ("city", "town", "village", "municipality", "suburb", "county")
                    if address.get(key)
                ),
                payload.get("display_name", "").split(",")[0],
            )
            if not name:
                raise ProviderError("No nearby place was found")

            location = Location(
                id=payload.get("place_id", 0),
                name=name,
                country=address.get("country", ""),
                admin1=address.get("state") or address.get("region"),
                latitude=latitude,
                longitude=longitude,
                timezone="UTC",
            )
            _cache[cache_key] = (monotonic() + CACHE_TTL_SECONDS, location)
            if len(_cache) > 256:
                now = monotonic()
                expired = [key for key, (expiry, _) in _cache.items() if expiry <= now]
                for key in expired:
                    _cache.pop(key, None)
                if len(_cache) > 256:
                    _cache.pop(next(iter(_cache)))
            return location

    @asynccontextmanager
    async def _client_scope(self) -> AsyncIterator[httpx.AsyncClient]:
        if self._client is not None:
            yield self._client
            return
        async with httpx.AsyncClient(
            timeout=5.0,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            yield client
