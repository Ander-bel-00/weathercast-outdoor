# ADR 0004: Nearby weather layers on the map

## Status

Accepted

## Context

The map started as a point picker. WeatherCast also needs spatial context that lets a visitor compare conditions around a selected place without making a provider request for every visible point or changing the map into a full-screen radar product.

## Decision

- Keep Leaflet and the attributed OpenStreetMap base map.
- Render a 3 × 3 grid of weather comparison points inside the visible local map area.
- Offer temperature, hourly rain probability, and wind speed as mutually exclusive layers. Point size and color communicate relative values; a popup exposes all three values.
- When map movement settles, the browser sends the viewport bounds to FastAPI. The API validates the bounds and creates exactly nine coordinates. The Open-Meteo adapter requests those coordinates together and maps provider responses to the app's `WeatherMapPoint` schema.
- Debounce map movement in the browser and abort superseded requests. Require a local zoom level and reject very large bounds rather than returning a misleading sparse world-scale layer.
- Keep clicking the map surface as the location-selection gesture. Weather markers stop click propagation so inspecting a point does not dismiss the map.

## Consequences

- One settled viewport update uses one HTTP request to Open-Meteo, with nine requested coordinates. It is not one request per marker.
- The points are model-grid samples and should be described as local forecast context, not station observations or precipitation radar.
- The standard OpenStreetMap tile service remains appropriate only for modest demo traffic; use a suitable tile provider before scaling.
- Provider parsing remains isolated in `OpenMeteoClient`, and API route tests can inject a fake client without network access.
