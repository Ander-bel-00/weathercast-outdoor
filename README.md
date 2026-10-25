# WeatherCast

WeatherCast is an open-source weather context dashboard that helps people decide what to do outdoors. It combines a forecast with small, explainable activity recommendations instead of presenting weather data without context.

> **Early project:** this repository is the start of the MVP. Recommendations are informational heuristics, not professional weather, medical, or aviation advice.

## Product direction

- Search for a city and inspect current conditions plus the next 24 hours.
- Read the hourly temperature and rain trend in a chart, with a weather scene that adapts to current conditions.
- Follow a subtle local-time atmosphere: a soft morning or afternoon sky, a restrained evening tint, and stars at night. The forecast scene remains tied to actual weather conditions.
- See why a walk, run, or bike ride is recommended or discouraged.
- Get nearby weather automatically after granting browser location permission; preferences for language and theme stay in the browser.
- Explore conditions on an interactive map and compare nearby places (next milestones).
- Configure personal thresholds and alerts after the core experience is reliable.

The differentiator is **decision context with visible reasoning**: each recommendation should show the conditions behind it and let people adjust thresholds. The first release uses deterministic rules; it does not claim to use AI.

## Stack

- **API:** Python, FastAPI, Pydantic, HTTPX; Open-Meteo forecast and geocoding APIs.
- **Web:** Vue 3 with Nuxt 3, TypeScript, Tailwind CSS.
- **Map:** Leaflet with OpenStreetMap tiles (planned for the map milestone).
- **Deployment direction:** Docker Compose managed by Coolify on the Hetzner CAX21 VPS. Build and deploy ARM64-compatible images; Coolify will provide the public routing and HTTPS configuration.

We are starting as a modular monolith. That keeps the first deployment and learning loop simple while preserving boundaries between HTTP routes, provider integration, domain rules, and the UI.

## Run locally

Requirements: Python 3.12+, Node.js 20+, and npm.

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

In a second terminal:

```sh
cd frontend
npm install
npm run dev
```

The API is at `http://localhost:8000`; interactive API documentation is at `/docs`. The web app is at `http://localhost:3000`. The frontend accepts `NUXT_PUBLIC_API_BASE` if the API runs elsewhere.

Open-Meteo forecast data is shown with attribution and GeoNames is credited for geocoding. The free Open-Meteo API is limited to non-commercial use; review its current terms before using this project commercially or scaling traffic.

Current coordinates are sent to Open-Meteo for a forecast and to OpenStreetMap Nominatim to identify a nearby place. The app asks the browser for permission, shows a fallback city if access is denied, caches reverse lookups, and credits OpenStreetMap. See [the location and preferences decision](docs/decisions/0002-location-and-preferences.md).

## Repository map

```text
backend/     FastAPI application and weather domain
frontend/    Nuxt application
docs/        decisions, product scope, and contribution workflow
```

## Development workflow

- Keep `main` releasable. Work in short-lived branches named `feat/...`, `fix/...`, `docs/...`, or `chore/...`.
- Use [Conventional Commits](https://www.conventionalcommits.org/), for example `feat(api): add city search`.
- Keep provider-specific parsing in the provider adapter. Keep activity rules independent from FastAPI and HTTP clients.
- Explain meaningful architectural choices in `docs/decisions/` and update the README when setup or product behavior changes.
- Prefer small pull requests with a clear problem statement, screenshots for UI changes, and a verification note.

See [the product and learning roadmap](docs/ROADMAP.md), [portfolio project series](docs/PORTFOLIO.md), [architecture decisions](docs/decisions/), and [contribution guide](CONTRIBUTING.md).

## Portfolio series ideas

WeatherCast is project one in a portfolio that can show distinct engineering skills: a data analysis story with reproducible notebooks; a polished public API integration; an inventory and low-stock workflow; a small commerce/catalog experience; a vehicle marketplace with search and saved listings; a game-related stats or companion tool; and a developer utility with a CLI plus web UI. Each project should solve a focused problem and include a live demo, concise documentation, and a short write-up of trade-offs.
