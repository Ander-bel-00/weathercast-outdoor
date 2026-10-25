# ADR 0003: Base outdoor guidance on the next three hours

- **Status:** Accepted
- **Decision:** Use deterministic, documented activity guidance from current conditions and the next three hourly forecast points. Keep the rules inside the API domain layer and return concrete, localized reasons with the recommendation.
- **Context:** A user should not need to tune meteorological thresholds to understand a recommendation. Generic text such as “some precipitation is expected” does not help someone decide when to leave or whether to wait.
- **Signals:** Forecast rain probability and its forecast time, the maximum hourly wind speed in the selected horizon, current feels-like temperature, current precipitation, and current thunderstorm codes.
- **Activity rules:** Walking uses a 35 km/h wind guide and rain guidance at 40%/80% (caution/wait); running uses 30 km/h and 45%/75%; cycling uses 25 km/h and 30%/65%. Temperature comfort ranges vary by activity and live beside the rules in `backend/app/domain/recommendations.py`.
- **Consequences:** Reasons can say “rain probability reaches 85% at 14:00 in the next 3 hours” instead of only saying precipitation is expected. Advice stays informational, uses provider forecast data, and does not replace official alerts or professional safety guidance. If hourly data is missing, the API explicitly lowers confidence and says that only current conditions were used.
- **UI flow:** Keep current weather and activity advice as the primary view. Open the interactive map in a modal so it does not push those answers down the page; selecting a map point closes the modal, loads its forecast, and returns the user to the updated summary.
