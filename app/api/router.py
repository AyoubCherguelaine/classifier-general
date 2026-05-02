from fastapi import APIRouter

from app.routers import classification, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(classification.router)
