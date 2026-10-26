from datetime import datetime

from app.domain.recommendations import recommend_activities
from app.schemas.weather import CurrentConditions, HourlyPoint


def conditions(**overrides: float) -> CurrentConditions:
    values = {
        "time": "2026-10-25T12:00:00",
        "temperature_c": 22,
        "apparent_temperature_c": 21,
        "relative_humidity_pct": 60,
        "precipitation_mm": 0,
        "wind_speed_kmh": 5,
        "weather_code": 1,
    }
    values.update(overrides)
    return CurrentConditions(**values)


def hour(hour: int, *, rain_chance: int = 5, wind_speed: float = 5) -> HourlyPoint:
    return HourlyPoint(
        time=datetime(2026, 10, 25, hour),
        temperature_c=22,
        precipitation_probability_pct=rain_chance,
        wind_speed_kmh=wind_speed,
    )


def test_favorable_weather_explains_the_forecast_horizon() -> None:
    recommendations = recommend_activities(
        conditions(), [hour(12), hour(13), hour(14), hour(15)], "en"
    )

    assert [item.activity for item in recommendations] == ["walk", "run", "bike"]
    assert {item.rating for item in recommendations} == {"good"}
    assert all("next 3 hours" in item.reasons[0] for item in recommendations)


def test_high_rain_probability_explains_when_to_wait() -> None:
    recommendations = recommend_activities(
        conditions(), [hour(12), hour(13, rain_chance=40), hour(14, rain_chance=85)], "en"
    )

    assert all(item.rating == "poor" for item in recommendations)
    assert all(
        "85%" in item.reasons[0] and "2:00 PM" in item.reasons[0] for item in recommendations
    )
    assert all("Waiting is safer" in item.reasons[0] for item in recommendations)


def test_wind_forecast_changes_bike_advice_with_concrete_speed_and_time() -> None:
    recommendations = recommend_activities(
        conditions(), [hour(12), hour(13), hour(14, wind_speed=28)], "en"
    )

    bike = recommendations[2]
    assert bike.rating == "poor"
    assert "28 km/h at 2:00 PM" in bike.reasons[0]


def test_current_rain_and_heat_are_explained_in_spanish() -> None:
    recommendations = recommend_activities(
        conditions(precipitation_mm=0.4, apparent_temperature_c=37), [hour(12)], "es"
    )

    walk = recommendations[0]
    assert walk.rating == "caution"
    assert "Está lloviendo ahora (se registran 0.4 mm)." in walk.reasons
    assert any("sensación térmica es de 37 °C" in reason for reason in walk.reasons)


def test_thunderstorm_recommends_waiting() -> None:
    recommendations = recommend_activities(conditions(weather_code=95), [hour(12)], "es")

    assert all(item.rating == "poor" for item in recommendations)
    assert all("tormenta eléctrica" in item.reasons[-1] for item in recommendations)


def test_missing_hourly_forecast_does_not_claim_future_conditions() -> None:
    recommendations = recommend_activities(conditions(), [], "en")

    assert all(item.rating == "caution" for item in recommendations)
    assert all("current conditions only" in item.reasons[-1] for item in recommendations)
