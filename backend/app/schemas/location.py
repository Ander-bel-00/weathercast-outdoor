from pydantic import BaseModel


class Location(BaseModel):
    id: int
    name: str
    country: str
    admin1: str | None = None
    latitude: float
    longitude: float
    timezone: str
