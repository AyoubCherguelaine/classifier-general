import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import ClassificationError
from app.services.classifier_service import classifier_service

logger = logging.getLogger(__name__)

settings.static_dir.mkdir(parents=True, exist_ok=True)
settings.upload_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.include_router(api_router)


@app.on_event("startup")
def preload_classifier_model() -> None:
    try:
        classifier_service.warmup()
        logger.info("Classifier model preloaded on startup")
    except ClassificationError:
        logger.exception("Classifier model warmup failed")


@app.get("/endpoint/")
def list_endpoints() -> list[dict]:
    endpoints = []
    for route in app.routes:
        methods = sorted((route.methods or set()) & {"GET", "POST", "PUT", "DELETE"})
        if methods:
            endpoints.append({"endpoint": route.path, "methods": methods})
    return endpoints
