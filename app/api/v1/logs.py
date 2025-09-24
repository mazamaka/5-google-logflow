from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.batch import BatchRequest
from app.services.db_logging import process_batch
from app.core.logging_config import logger

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/batch", status_code=status.HTTP_200_OK)
async def logs_batch(req: BatchRequest, session: AsyncSession = Depends(get_db_session)) -> dict:
    try:
        logger.info(
            f"[api] POST /api/v1/logs/batch run_id={req.run_id} task_id={req.task_id} action={req.action_name} logs={len(req.logs)}"
        )
        count = await process_batch(session, req)
        logger.info(f"[api] stored batch run_id={req.run_id} inserted={count}")
        return {"status": "ok", "received_logs": count}
    except Exception as e:  # noqa: BLE001
        logger.exception(f"[api] failed to process batch run_id={req.run_id}")
        raise HTTPException(status_code=500, detail="Ошибка при записи в БД") from e
