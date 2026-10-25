# Product and learning roadmap

## MVP: a useful forecast, not a weather clone

1. Search for a city and load its current, hourly, and seven-day conditions.
2. Show selectable daily summaries and an hourly temperature and rain chart for the selected day, plus a condition-specific visual scene.
3. Detect the visitor's location after browser permission, with a useful fallback when permission is denied.
4. Let visitors choose English or Spanish and system, light, or dark appearance.
5. Show clear loading, empty, and error states.
6. Explain outdoor activity suggestions with concrete weather factors from the current conditions and next three hours.
7. Keep the dashboard responsive, accessible, and clear about its data source and limits.

## Next milestones

### Map and spatial context

- **Implemented:** compare nine forecast points in the visible map area with temperature, rain-probability, and wind layers. Choosing a point loads the full hourly and daily forecast.
- **Implemented:** batch all nine coordinate pairs into one forecast-provider request after map movement settles; cancel stale requests in the browser and reject oversized map bounds in the API.
- **Next:** show a visible data timestamp and consider a weather-tile provider if usage grows beyond a small portfolio demo.
- Respect OpenStreetMap tile attribution and usage policy; avoid treating the standard tile service as a free bulk tile CDN.

### Personalization and data quality

- Add caching, provider timeouts, rate-limit handling, and a visible last-updated time.
- Track provider attribution and forecast freshness.

### Portfolio polish

- Add repeatable browser-level checks for city search, geolocation permission states, map layer selection, and narrow viewports.
- Add provider freshness/availability monitoring.
- Publish the Coolify deployment and verify ARM64 images on the CAX21.
- Add release screenshots and publish a short case study explaining what was learned.

## Product boundaries

The app offers general outdoor-planning context. It is not an emergency-alert service or a substitute for official forecasts. Do not use the activity score for aviation decisions. Any future alerting should clearly identify its source and delivery delay.

## Learning goals

Build the project in visible slices: Python API boundaries and data validation; consuming and normalizing a third-party API; Vue/Nuxt state and accessibility; map interaction and geospatial display; then deployment, observability, and documentation. Prefer a small working vertical slice over a large, disconnected architecture.
