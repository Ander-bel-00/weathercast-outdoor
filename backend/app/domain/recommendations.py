from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from app.schemas.weather import (
    ActivityRecommendation,
    CurrentConditions,
    HourlyPoint,
)

HORIZON_HOURS = 3


@dataclass(frozen=True, slots=True)
class ActivityRule:
    activity: Literal["walk", "run", "bike"]
    max_wind_kmh: float
    rain_caution_pct: int
    rain_wait_pct: int
    cold_feels_like_c: float
    hot_feels_like_c: float
    extreme_heat_c: float


ACTIVITY_RULES = (
    ActivityRule("walk", 35, 40, 80, 3, 35, 40),
    ActivityRule("run", 30, 45, 75, 5, 32, 38),
    ActivityRule("bike", 25, 30, 65, 7, 30, 36),
)

MESSAGES = {
    "en": {
        "wind_wait": (
            "Wind is forecast to reach {value} km/h at {time} in the next 3 hours; "
            "waiting is safer for this activity."
        ),
        "wind_wait_now": "Wind is {value} km/h now; waiting is safer for this activity.",
        "wind_caution": "Wind may reach {value} km/h at {time} in the next 3 hours.",
        "wind_caution_now": "Wind is {value} km/h now, so take care with this activity.",
        "rain_wait": (
            "Rain probability reaches {chance}% at {time} in the next 3 hours. Waiting is safer."
        ),
        "rain_caution": (
            "Rain probability reaches {chance}% at {time} in the next 3 hours; plan for rain."
        ),
        "rain_now": "It is raining now ({value} mm recorded).",
        "cold": "Feels like {value} °C now; dress warmly for this activity.",
        "hot": "Feels like {value} °C now; take water and avoid the hottest hours.",
        "extreme_heat": "Feels like {value} °C now; it is safer to wait for cooler conditions.",
        "storm": "A thunderstorm is reported now. Wait until it has passed.",
        "clear": "No high wind or meaningful rain is expected in the next 3 hours.",
        "no_hourly": (
            "The hourly outlook is unavailable; this suggestion uses current conditions only."
        ),
        "now": "now",
    },
    "es": {
        "wind_wait": (
            "Se esperan vientos de {value} km/h a las {time}, durante las próximas 3 horas; "
            "es mejor esperar para esta actividad."
        ),
        "wind_wait_now": (
            "El viento está en {value} km/h ahora; es mejor esperar para esta actividad."
        ),
        "wind_caution": (
            "El viento podría llegar a {value} km/h a las {time}, durante las próximas 3 horas."
        ),
        "wind_caution_now": (
            "El viento está en {value} km/h ahora; ten precaución con esta actividad."
        ),
        "rain_wait": (
            "La probabilidad de lluvia llega al {chance}% a las {time}, durante las próximas "
            "3 horas. Es mejor esperar."
        ),
        "rain_caution": (
            "La probabilidad de lluvia llega al {chance}% a las {time}, durante las próximas "
            "3 horas; planea con lluvia."
        ),
        "rain_now": "Está lloviendo ahora (se registran {value} mm).",
        "cold": "La sensación térmica es de {value} °C; abrígate para esta actividad.",
        "hot": "La sensación térmica es de {value} °C; lleva agua y evita las horas más calurosas.",
        "extreme_heat": (
            "La sensación térmica es de {value} °C; es más seguro esperar a que refresque."
        ),
        "storm": "Hay una tormenta eléctrica ahora. Espera a que pase.",
        "clear": "No se esperan lluvias importantes ni viento fuerte durante las próximas 3 horas.",
        "no_hourly": (
            "No hay pronóstico por hora; esta sugerencia usa solo las condiciones actuales."
        ),
        "now": "ahora",
    },
}


def recommend_activities(
    current: CurrentConditions,
    hourly: list[HourlyPoint],
    language: Literal["en", "es"] = "en",
) -> list[ActivityRecommendation]:
    """Explain outdoor guidance using current conditions and the next three hourly points."""
    outlook = [point for point in hourly if point.time >= current.time][:HORIZON_HOURS]
    return [_recommend_activity(rule, current, outlook, language) for rule in ACTIVITY_RULES]


def _recommend_activity(
    rule: ActivityRule,
    current: CurrentConditions,
    outlook: list[HourlyPoint],
    language: Literal["en", "es"],
) -> ActivityRecommendation:
    messages = MESSAGES[language]
    reasons: list[str] = []
    severe = False
    caution = False

    wind_point = max(outlook, key=lambda point: point.wind_speed_kmh, default=None)
    wind_speed = max(current.wind_speed_kmh, wind_point.wind_speed_kmh if wind_point else 0)
    wind_is_forecast = (
        wind_point is not None and wind_point.wind_speed_kmh >= current.wind_speed_kmh
    )
    wind_time = _format_time(wind_point.time, language) if wind_is_forecast else messages["now"]
    if wind_speed >= rule.max_wind_kmh:
        wind_reason = "wind_wait" if wind_is_forecast else "wind_wait_now"
        reasons.append(messages[wind_reason].format(value=f"{wind_speed:g}", time=wind_time))
        severe = True
    elif wind_speed >= rule.max_wind_kmh * 0.75:
        wind_reason = "wind_caution" if wind_is_forecast else "wind_caution_now"
        reasons.append(messages[wind_reason].format(value=f"{wind_speed:g}", time=wind_time))
        caution = True

    rain_point = max(
        outlook,
        key=lambda point: point.precipitation_probability_pct,
        default=None,
    )
    rain_probability = rain_point.precipitation_probability_pct if rain_point else 0
    if rain_point and rain_probability >= rule.rain_wait_pct:
        reasons.append(
            messages["rain_wait"].format(
                chance=rain_probability,
                time=_format_time(rain_point.time, language),
            )
        )
        severe = True
    elif rain_point and rain_probability >= rule.rain_caution_pct:
        reasons.append(
            messages["rain_caution"].format(
                chance=rain_probability,
                time=_format_time(rain_point.time, language),
            )
        )
        caution = True
    elif current.precipitation_mm > 0:
        reasons.append(messages["rain_now"].format(value=f"{current.precipitation_mm:g}"))
        caution = True

    if current.weather_code >= 95:
        reasons.append(messages["storm"])
        severe = True

    feels_like = current.apparent_temperature_c
    if feels_like <= rule.cold_feels_like_c:
        reasons.append(messages["cold"].format(value=f"{feels_like:g}"))
        caution = True
    if feels_like >= rule.extreme_heat_c:
        reasons.append(messages["extreme_heat"].format(value=f"{feels_like:g}"))
        severe = True
    elif feels_like >= rule.hot_feels_like_c:
        reasons.append(messages["hot"].format(value=f"{feels_like:g}"))
        caution = True

    if not outlook:
        reasons.append(messages["no_hourly"])
        caution = True
    if not reasons:
        reasons.append(messages["clear"])

    rating = "poor" if severe else "caution" if caution else "good"
    return ActivityRecommendation(activity=rule.activity, rating=rating, reasons=reasons)


def _format_time(value: datetime, language: Literal["en", "es"]) -> str:
    if language == "es":
        return value.strftime("%H:%M")
    return value.strftime("%I:%M %p").lstrip("0")
