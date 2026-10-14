from fastapi import APIRouter
from backend.api import health, podcast, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(podcast.router, prefix="/api", tags=["podcast"])
api_router.include_router(ui.router, tags=["ui"])
