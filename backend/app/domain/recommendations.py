from typing import Literal

from app.schemas.weather import ActivityRecommendation, CurrentConditions

MESSAGES = {
    "en": {
        "wind_strong": "Wind is strong at {value} km/h",
        "wind_comfort": "Wind may affect comfort at {value} km/h",
        "rain": "Precipitation is {value} mm",
        "rain_some": "Some precipitation is expected",
        "cold": "Feels cold at {value} °C",
        "clear": "No major wind, rain, or cold-weather factor right now",
    },
    "es": {
        "wind_strong": "El viento es fuerte: {value} km/h",
        "wind_comfort": "El viento puede afectar la comodidad: {value} km/h",
        "rain": "La precipitación es de {value} mm",
        "rain_some": "Se espera algo de precipitación",
        "cold": "La sensación térmica es fría: {value} °C",
        "clear": "No hay factores importantes de viento, lluvia o frío por ahora",
    },
}


def recommend_activities(
    current: CurrentConditions,
    language: Literal["en", "es"] = "en",
) -> list[ActivityRecommendation]:
    """Apply transparent, deliberately simple outdoor-planning heuristics."""
    return [
        _rate_activity("walk", current, language, wind_limit=35, rain_limit=2.0, low_temp=3),
        _rate_activity("run", current, language, wind_limit=30, rain_limit=1.5, low_temp=5),
        _rate_activity("bike", current, language, wind_limit=25, rain_limit=0.5, low_temp=7),
    ]


def _rate_activity(
    activity: str,
    current: CurrentConditions,
    language: Literal["en", "es"],
    *,
    wind_limit: float,
    rain_limit: float,
    low_temp: float,
) -> ActivityRecommendation:
    messages = MESSAGES[language]
    reasons: list[str] = []
    severe = False
    caution = False

    if current.wind_speed_kmh >= wind_limit:
        reasons.append(messages["wind_strong"].format(value=f"{current.wind_speed_kmh:g}"))
        severe = True
    elif current.wind_speed_kmh >= wind_limit * 0.7:
        reasons.append(messages["wind_comfort"].format(value=f"{current.wind_speed_kmh:g}"))
        caution = True

    if current.precipitation_mm >= rain_limit:
        reasons.append(messages["rain"].format(value=f"{current.precipitation_mm:g}"))
        severe = True
    elif current.precipitation_mm > 0:
        reasons.append(messages["rain_some"])
        caution = True

    if current.apparent_temperature_c < low_temp:
        reasons.append(messages["cold"].format(value=f"{current.apparent_temperature_c:g}"))
        caution = True

    if not reasons:
        reasons.append(messages["clear"])

    rating = "poor" if severe else "caution" if caution else "good"
    return ActivityRecommendation(activity=activity, rating=rating, reasons=reasons)
