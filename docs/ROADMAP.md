# Product and learning roadmap

## MVP: a useful forecast, not a weather clone

1. Search for a city and load its current and hourly conditions.
2. Show clear loading, empty, and error states.
3. Explain outdoor activity suggestions with the forecast factors that affected them.
4. Add a responsive, accessible dashboard and document the data source and its limits.

## Next milestones

### Map and spatial context

- Add a Leaflet map with selectable places and weather overlays.
- Compare a few nearby points and show when/where each forecast was fetched.
- Respect OpenStreetMap tile attribution and usage policy; avoid treating the standard tile service as a free bulk tile CDN.

### Personalization and data quality

- Let people adjust thresholds (wind, precipitation, temperature) and save preferences.
- Add caching, provider timeouts, rate-limit handling, and a visible last-updated time.
- Track provider attribution and forecast freshness.

### Portfolio polish

- Add CI for formatting, linting, type checks, and unit tests.
- Add Docker Compose for Coolify, verify ARM64-compatible images for the CAX21, document backups and operations, then publish a demo on the VPS.
- Publish architecture notes and a short case study explaining what was learned.

## Product boundaries

The app offers general outdoor-planning context. It is not an emergency-alert service or a substitute for official forecasts. Do not use the activity score for aviation decisions. Any future alerting should clearly identify its source and delivery delay.

## Learning goals

Build the project in visible slices: Python API boundaries and data validation; consuming and normalizing a third-party API; Vue/Nuxt state and accessibility; map interaction and geospatial display; then deployment, observability, and documentation. Prefer a small working vertical slice over a large, disconnected architecture.
