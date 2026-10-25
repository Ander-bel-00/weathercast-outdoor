import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

app = FastAPI(
    title="WeatherCast API",
    description="Weather context and explainable outdoor activity guidance.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["operations"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
