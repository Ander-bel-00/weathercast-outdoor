import asyncio
from time import monotonic

import httpx
import pytest

from app.providers import nominatim
from app.providers.errors import ProviderError
from app.providers.nominatim import NominatimClient


def test_reverse_geocoder_returns_place_and_reuses_cached_result(monkeypatch) -> None:
    nominatim._cache.clear()
    monkeypatch.setattr(nominatim, "_last_request_at", monotonic() - 2)

    async def scenario() -> tuple[object, object, list[httpx.Request]]:
        requests: list[httpx.Request] = []

        def respond(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(
                200,
                json={
                    "place_id": 123,
                    "display_name": "Dosquebradas, Colombia",
                    "address": {
                        "municipality": "Dosquebradas",
                        "state": "Risaralda",
                        "country": "Colombia",
                    },
                },
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            geocoder = NominatimClient(client)
            first = await geocoder.reverse(4.8401, -75.6701, "es")
            second = await geocoder.reverse(4.8402, -75.6702, "es")
        return first, second, requests

    first, second, requests = asyncio.run(scenario())
    nominatim._cache.clear()

    assert first.name == "Dosquebradas"
    assert first.admin1 == "Risaralda"
    assert first.country == "Colombia"
    assert second.latitude == 4.8402
    assert second.longitude == -75.6702
    assert len(requests) == 1


def test_reverse_geocoder_wraps_http_errors(monkeypatch) -> None:
    nominatim._cache.clear()
    monkeypatch.setattr(nominatim, "_last_request_at", monotonic() - 2)

    async def scenario() -> None:
        def respond(_: httpx.Request) -> httpx.Response:
            return httpx.Response(503)

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            await NominatimClient(client).reverse(40.7, -74.0, "en")

    with pytest.raises(ProviderError):
        asyncio.run(scenario())
