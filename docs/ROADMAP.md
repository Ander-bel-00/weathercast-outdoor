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

### Release candidate: implemented

- **Implemented:** explainable walk, run, and cycling guidance derived from current conditions and the next three hours. The app applies its own activity-specific weather rules; visitors do not need to configure meteorological thresholds.
- **Implemented:** a seven-day outlook, hourly chart, nearby weather map layers, responsive layout, English/Spanish copy, and system/light/dark themes.
- **Implemented:** backend and frontend quality checks in GitHub Actions, a Docker Compose health check, and a Coolify deployment guide.
- **Release checks:** review the pull request and its CI checks, merge the reviewed branch into `main`, deploy that commit to Coolify, then add production screenshots and the public URL here and in the README.

### Map and spatial context

- **Implemented:** compare nine forecast points in the visible map area with temperature, rain-probability, and wind layers. Choosing a point loads the full hourly and daily forecast.
- **Implemented:** batch all nine coordinate pairs into one forecast-provider request after map movement settles; cancel stale requests in the browser and reject oversized map bounds in the API.
- **Next:** consider a weather-tile provider if usage grows beyond a small portfolio demo.
- Respect OpenStreetMap tile attribution and usage policy; avoid treating the standard tile service as a free bulk tile CDN.

### Data quality and future improvements

- Add caching and provider rate-limit handling if usage grows.
- Monitor provider availability and forecast freshness after the first deployment.

### Portfolio polish

- Add repeatable browser-level checks for city search, geolocation permission states, map layer selection, and narrow viewports.
- Publish the Coolify deployment and verify ARM64 images on the CAX21.
- Add release screenshots and publish a short case study explaining what was learned.

## Product boundaries

The app offers general outdoor-planning context. It is not an emergency-alert service or a substitute for official forecasts. Do not use the activity score for aviation decisions. Any future alerting should clearly identify its source and delivery delay.

## Learning goals

Build the project in visible slices: Python API boundaries and data validation; consuming and normalizing a third-party API; Vue/Nuxt state and accessibility; map interaction and geospatial display; then deployment, observability, and documentation. Prefer a small working vertical slice over a large, disconnected architecture.
