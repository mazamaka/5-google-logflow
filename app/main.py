from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging_config import logger
from app.services.minio_service import get_minio_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: ensure MinIO bucket exists on startup."""
    try:
        svc = get_minio_service()
        await svc.ensure_bucket_async()
    except Exception as e:  # noqa: BLE001
        logger.warning("[startup] MinIO ensure_bucket failed: {}", e)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)
