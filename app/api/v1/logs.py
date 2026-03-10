from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.logging_config import logger
from app.schemas.batch import BatchRequest
from app.services.db_logging import process_batch

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/batch", status_code=status.HTTP_200_OK)
async def logs_batch(
    req: BatchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    """Ingest a batch of log entries for a given automation run."""
    try:
        logger.info(
            "[api] POST /logs/batch run_id={} logs={}",
            req.run_id, len(req.logs),
        )
        count = await process_batch(session, req)
        return {"status": "ok", "received_logs": count}
    except Exception as e:  # noqa: BLE001
        logger.exception("[api] batch failed run_id={}", req.run_id)
        raise HTTPException(status_code=500, detail="Log ingestion failed") from e
