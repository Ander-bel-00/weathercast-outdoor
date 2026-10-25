# Contributing

Thanks for helping improve WeatherCast. Keep contributions focused and explain the user problem they solve.

## Branches and commits

Use a short branch from `main`: `feat/city-search`, `fix/empty-forecast`, `docs/local-setup`, or `chore/ci`. Use Conventional Commit messages such as `feat(web): add accessible city search`.

## Pull requests

Include the context, approach, and any trade-offs. For visual changes, add a screenshot. Mention what you verified locally. Update documentation when behavior or setup changes. Avoid mixing unrelated refactors into feature changes.

## Engineering principles

- Keep I/O at the edges: provider clients perform network requests; domain rules work on validated data.
- Make recommendations explainable and conservative. Add the factors that led to every outcome.
- Keep UI states explicit: loading, empty, success, and error.
- Treat external API responses as untrusted input and handle provider failures gracefully.
