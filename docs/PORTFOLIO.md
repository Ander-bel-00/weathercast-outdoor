# Portfolio project series

The goal is to show range through a few complete, useful projects—not to start many half-finished repositories. Give every project a clear user, one memorable feature, a live demo when practical, a screenshot, setup instructions, and a short case study about trade-offs.

## Suggested order

| Project | What it solves | Skills it makes visible |
| --- | --- | --- |
| **WeatherCast** | Helps people plan outdoor activities using forecast context and explainable guidance. | Python API, third-party data, Vue/Nuxt, charts/maps, deployment. |
| **City Signals** | Tells a compact data story about heat, rain, or air quality across cities and years. | Data cleanup, Pandas, analysis notebooks, chart design, reproducibility. |
| **OpenShelf** | Makes it easier to discover books by combining an external books API with thoughtful search and saved lists. | API integration, caching, pagination, error handling, responsive UI. |
| **Stockroom** | Tracks stock movements and warns a small shop before popular items run out. | Relational modeling, authentication, transactions, audit history, role-based access. |
| **Mileage Compass** | Lets people filter car listings, save a shortlist, and compare total ownership factors. | Search/filter design, database queries, forms, user workflows, accessible UI. |
| **PatchNotes** | Summarizes a player's game backlog and recent releases from public data sources. | API normalization, background refresh, data visualization, practical product thinking. |
| **Payload Bench** | Compares, validates, and prettifies JSON locally, with a small CLI for developer workflows. | TypeScript, parsing, edge cases, command-line UX, packaging and documentation. |

## Keep each project focused

1. Write a one-sentence problem and identify who it helps.
2. Build one complete user journey before adding more features.
3. Add polish that has a reason: accessibility, speed, useful empty/error states, responsive layout, clear data provenance.
4. Publish a demo and a short engineering write-up once the project is dependable.
5. Pick a different primary learning goal for each project so the portfolio shows range without repeating the same CRUD app.

For WeatherCast, the memorable feature is the traceable recommendation: users see the forecast factors and can eventually personalize the thresholds. The MVP uses deterministic logic; an “AI” label should only appear if a later feature uses a real model and explains what it adds.
