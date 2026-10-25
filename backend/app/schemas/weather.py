from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CurrentConditions(BaseModel):
    time: datetime
    temperature_c: float
    apparent_temperature_c: float
    relative_humidity_pct: int
    precipitation_mm: float
    wind_speed_kmh: float
    weather_code: int


class HourlyPoint(BaseModel):
    time: datetime
    temperature_c: float
    precipitation_probability_pct: int
    wind_speed_kmh: float


class DailyForecast(BaseModel):
    date: date
    weather_code: int
    temperature_max_c: float
    temperature_min_c: float
    precipitation_probability_max_pct: int
    precipitation_sum_mm: float
    wind_speed_max_kmh: float


class WeatherMapPoint(BaseModel):
    latitude: float
    longitude: float
    time: datetime
    temperature_c: float
    precipitation_probability_pct: int
    wind_speed_kmh: float
    weather_code: int


class ActivityRecommendation(BaseModel):
    activity: Literal["walk", "run", "bike"]
    rating: Literal["good", "caution", "poor"]
    reasons: list[str]


class WeatherRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location_name: str = Field(min_length=1, max_length=100)
    language: Literal["en", "es"] = "en"


class WeatherReport(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    timezone: str
    fetched_at: datetime
    current: CurrentConditions
    hourly: list[HourlyPoint]
    daily: list[DailyForecast]
    recommendations: list[ActivityRecommendation] = Field(default_factory=list)
