# WeatherCast

WeatherCast is an open-source weather context dashboard that helps people decide what to do outdoors. It combines a forecast with small, explainable activity recommendations instead of presenting weather data without context.

> **Early project:** this repository is the start of the MVP. Recommendations are informational heuristics, not professional weather, medical, or aviation advice.

## Product direction

- Search for a city and inspect current conditions, a seven-day outlook, and an hourly forecast for the selected day.
- Read the hourly temperature and rain trend in a chart, with a weather scene that adapts to current conditions.
- Use a restrained animated backdrop that adapts to the selected light or dark theme, while the forecast scene stays tied to actual weather conditions.
- See whether a walk, run, or bike ride is a good idea, with specific reasons from the weather now and the next three hours.
- Get nearby weather automatically after granting browser location permission; preferences for language and theme stay in the browser.
- Select a point on the interactive map to load its local forecast.

The differentiator is **decision context with visible reasoning**: each recommendation calls out forecast rain probability and time, wind, or feels-like temperature behind the advice. The rules are deterministic and deliberately transparent; the app does not claim to use AI.

## Stack

- **API:** Python, FastAPI, Pydantic, HTTPX; Open-Meteo forecast and geocoding APIs.
- **Web:** Vue 3 with Nuxt 3, TypeScript, Tailwind CSS.
- **Map:** Leaflet with attributed OpenStreetMap tiles.
- **Deployment:** Docker Compose managed by Coolify on the Hetzner CAX21 VPS. The Dockerfiles use ARM64-compatible base images; Coolify provides public routing and HTTPS.

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

## Run with Docker Compose

```sh
cp .env.example .env
docker compose -f compose.yaml -f compose.local.yaml up --build
```

This binds the local web and API ports to loopback. Open `http://localhost:3000`; the API docs are at `http://localhost:8000/docs`. For Coolify setup, environment variables, domains, health checks, and operational notes, see [the Coolify deployment guide](docs/deployment-coolify.md).

## Quality checks

```sh
cd backend
python -m pip install -e '.[dev]'
ruff check app tests
ruff format --check app tests
pytest --cov=app --cov-report=term-missing --cov-fail-under=80

cd ../frontend
npm ci
npm run typecheck
npm test
npm run build
```

GitHub Actions runs these API checks and the frontend type check and production build on pushes to `main` and pull requests targeting `main`.

Open-Meteo supplies the weather forecast and city search; OpenStreetMap Nominatim resolves nearby place names. The free Open-Meteo API is limited to non-commercial use; review its current terms before using this project commercially or scaling traffic.

Current coordinates or a point selected on the map are sent to Open-Meteo for a forecast. The app asks the browser for permission and shows a fallback city if access is denied. Map tiles come from the standard OpenStreetMap tile service and include visible attribution; keep usage appropriate for a small demo and follow its tile policy. See [the location and preferences decision](docs/decisions/0002-location-and-preferences.md).

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
