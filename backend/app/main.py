"""FastAPI entry point. Run with: uvicorn app.main:app --reload --port 8000"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import debris, health, hotlines, shelters, telemetry
from app.config import settings

app = FastAPI(title="AGAP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(telemetry.router)
app.include_router(hotlines.router)
app.include_router(shelters.router)
app.include_router(debris.router)
