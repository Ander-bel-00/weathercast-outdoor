from typing import Literal

from pydantic import BaseModel, Field


class Location(BaseModel):
    id: int
    name: str
    country: str
    admin1: str | None = None
    latitude: float
    longitude: float
    timezone: str


class ReverseLocationRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    language: Literal["en", "es"] = "en"
