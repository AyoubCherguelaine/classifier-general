from fastapi import APIRouter

from app.services.label_service import label_service

router = APIRouter(tags=["health"])


@router.get("/health/liveness")
def liveness() -> dict:
    return {"status": "ok"}


@router.get("/health/readiness")
def readiness() -> dict:
    # This service depends on external APIs, but readiness for local runtime
    # is based on successful startup and non-empty label config.
    labels = label_service.get_labels()
    return {"status": "ready", "labels_count": len(labels)}
