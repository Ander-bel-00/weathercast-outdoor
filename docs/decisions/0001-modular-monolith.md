# ADR 0001: Start with a modular monolith

- **Status:** Accepted
- **Decision:** Keep the web app and API as separate deployable packages in one repository, with the API organized into route, provider, and domain boundaries. Do not introduce microservices for the MVP.
- **Context:** The project is an individual learning and portfolio project, initially deployed to one 4-vCPU, 8-GB VPS. Independent services would add operational work before there is a demonstrated need.
- **Consequences:** Local development and deployment stay approachable. Modules can be extracted later if actual scaling or ownership needs justify the extra complexity.
