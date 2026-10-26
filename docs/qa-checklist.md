# WeatherCast release QA checklist

Use this checklist before merging a release candidate into `main`. Run the app over HTTPS or localhost so browser geolocation is available. Live weather and map checks require an internet connection.

## City search and forecast

- [ ] Type at least three characters. Suggestions appear only after typing pauses; each row includes city and region/country.
- [ ] Use Arrow Down/Arrow Up and Enter to select a suggestion. Confirm the selected location, current conditions, daily outlook, and chart update together.
- [ ] Type a name with no results and verify the localized empty state. Simulate an unavailable provider and verify the error stays near the search field.
- [ ] Submit the search form with Enter before choosing a suggestion; confirm the action does not send repeated requests.
- [ ] Select a future day and verify the chart contains only hours from that selected date.

## Location permission and preferences

- [ ] Allow browser location. Confirm nearby weather loads, the button leaves its loading state after coordinates arrive, and the place name can resolve independently.
- [ ] Deny browser location. Confirm the fallback city remains usable, the page explains the outcome, and the button can retry later.
- [ ] Leave the browser permission prompt unanswered. Confirm the UI wait limit releases the button and keeps the fallback forecast usable.
- [ ] Switch English/Spanish and System/Light/Dark. Refresh the page and confirm the saved settings remain selected and the full UI follows them.

## Weather map

- [ ] Open the map from the city search area. Confirm the modal owns keyboard focus and can close with its button or Escape.
- [ ] At local zoom, confirm nine nearby model-grid points load. Switch Temperature, Rain chance, and Wind; marker values and colors change without another grid request.
- [ ] Open a marker popup and confirm all three values are shown. Drag the map while the popup is open; the modal must remain open, the popup must close, and the new viewport must load points after movement settles.
- [ ] Zoom out past the local-layer limit. Confirm points clear and the zoom-in message appears instead of implying world coverage.
- [ ] Click an empty map location. Confirm the map closes and the main forecast updates for that point.
- [ ] Check OpenStreetMap attribution remains visible at desktop and narrow mobile widths.

## Layout and accessibility

- [ ] Check a narrow viewport around 375 px, a tablet width, and desktop. Confirm no horizontal page overflow, controls remain usable, and the modal map fits the viewport.
- [ ] Use keyboard-only navigation through search, settings, map controls, day cards, and chart points. Confirm focus remains visible.
- [ ] Enable reduced motion in the operating system and confirm decorative animations stop.

## Container smoke checks

- [ ] Build and start Compose; wait for both health checks.
- [ ] Confirm `GET /health` returns `{"status":"ok"}`, the web route returns HTTP 200, city search returns results, and `/api/v1/weather/map-grid` returns nine points for local bounds.
- [ ] For a release, test the same paths through the public HTTPS domain and inspect browser console/network errors.

## Data interpretation

Map markers are model-grid samples, not weather stations or radar. Activity recommendations are general deterministic guidance, not official alerts or aviation advice. Record provider outage behavior separately from application defects.
