from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.batch import BatchRequest
from app.services.db_logging import process_batch

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/batch", status_code=status.HTTP_200_OK)
async def logs_batch(req: BatchRequest, session: AsyncSession = Depends(get_db_session)) -> dict:
    try:
        count = await process_batch(session, req)
        return {"status": "ok", "received_logs": count}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Ошибка при записи в БД") from e
