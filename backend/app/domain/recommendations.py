from app.schemas.weather import ActivityRecommendation, CurrentConditions


def recommend_activities(
    current: CurrentConditions,
) -> list[ActivityRecommendation]:
    """Apply transparent, deliberately simple outdoor-planning heuristics."""
    return [
        _rate_activity("walk", current, wind_limit=35, rain_limit=2.0, low_temp=3),
        _rate_activity("run", current, wind_limit=30, rain_limit=1.5, low_temp=5),
        _rate_activity("bike", current, wind_limit=25, rain_limit=0.5, low_temp=7),
    ]


def _rate_activity(
    activity: str,
    current: CurrentConditions,
    *,
    wind_limit: float,
    rain_limit: float,
    low_temp: float,
) -> ActivityRecommendation:
    reasons: list[str] = []
    severe = False
    caution = False

    if current.wind_speed_kmh >= wind_limit:
        reasons.append(f"Wind is strong at {current.wind_speed_kmh:g} km/h")
        severe = True
    elif current.wind_speed_kmh >= wind_limit * 0.7:
        reasons.append(f"Wind may affect comfort at {current.wind_speed_kmh:g} km/h")
        caution = True

    if current.precipitation_mm >= rain_limit:
        reasons.append(f"Precipitation is {current.precipitation_mm:g} mm")
        severe = True
    elif current.precipitation_mm > 0:
        reasons.append("Some precipitation is expected")
        caution = True

    if current.apparent_temperature_c < low_temp:
        reasons.append(f"Feels cold at {current.apparent_temperature_c:g} °C")
        caution = True

    if not reasons:
        reasons.append("No major wind, rain, or cold-weather factor right now")

    rating = "poor" if severe else "caution" if caution else "good"
    return ActivityRecommendation(activity=activity, rating=rating, reasons=reasons)
