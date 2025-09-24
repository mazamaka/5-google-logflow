from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.logs import router as logs_router
from app.api.v1.runs import router as runs_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(logs_router)
api_router.include_router(runs_router)
