from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import settings
from app.services.minio_service import get_minio_service

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup() -> None:
    # На всякий случай гарантируем наличие bucket (основная подготовка в start.sh)
    try:
        svc = get_minio_service()
        await svc.ensure_bucket_async()
    except Exception as e:  # noqa: BLE001
        print(f"[startup] MinIO ensure_bucket failed: {e}")


# Подключаем агрегирующий маршрутизатор API v1
app.include_router(api_router)
