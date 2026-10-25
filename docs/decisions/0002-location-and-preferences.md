# ADR 0002: Respect location permission and keep display preferences local

- **Status:** Accepted
- **Decision:** Ask the browser for the user's current location to load nearby weather. If permission is unavailable or denied, show Dosquebradas as the initial fallback. Store the language and light/dark preference in browser local storage; do not store coordinates. Send coordinates in request bodies rather than URL query strings so application access logs do not record them.
- **Context:** A fixed Bogotá default is not useful to every user. Current coordinates provide a better forecast, while a reverse-geocoded city name makes the selected location understandable.
- **Provider boundaries:** Open-Meteo supplies weather and forward city search. OpenStreetMap Nominatim resolves coordinates to a nearby place through a server-side provider adapter. The endpoint is configurable, requests are serialized to at most one per second per process, and successful results are cached for six hours.
- **Privacy and attribution:** Location is requested through the browser permission prompt. Coordinates are sent to weather and nearby-place providers only after permission is granted. The interface discloses this behavior and links OpenStreetMap attribution.
- **Consequences:** The site needs HTTPS outside localhost for browser geolocation. Reverse lookup can fail independently, in which case the app still shows forecast data under a generic nearby-location label. Users can still search for a city manually.
