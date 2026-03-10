from __future__ import annotations

from collections.abc import Iterable
from datetime import timezone

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import logger
from app.models.automation_run import AutomationRun
from app.models.log import Log
from app.schemas.batch import BatchRequest, LogEntry


async def upsert_automation_run(
    session: AsyncSession,
    *,
    run_id: str,
    task_id: str,
    profile_id: str | None,
    action_name: str,
    task_data: dict | None,
    update_task_data: bool = True,
) -> None:
    """Insert or update automation run record."""
    logger.debug(
        "[db] upsert automation_run run_id={} task_id={} action={}",
        run_id, task_id, action_name,
    )
    update_fields: dict[str, object] = {
        "task_id": task_id,
        "profile_id": profile_id,
        "action_name": action_name,
    }
    if update_task_data:
        update_fields["task_data"] = task_data
    stmt = (
        pg_insert(AutomationRun)
        .values(
            run_id=run_id,
            task_id=task_id,
            profile_id=profile_id,
            action_name=action_name,
            task_data=task_data,
        )
        .on_conflict_do_update(
            index_elements=[AutomationRun.run_id],
            set_=update_fields,
        )
    )
    await session.execute(stmt)


def _prepare_rows(run_id: str, entries: Iterable[LogEntry]) -> list[dict]:
    rows: list[dict] = []
    for e in entries:
        ts = e.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        rows.append(
            {
                "run_id": run_id,
                "timestamp": ts,
                "level": e.level.value,
                "message": e.message,
                "data": e.data,
            }
        )
    return rows


async def insert_logs(session: AsyncSession, run_id: str, entries: Iterable[LogEntry]) -> int:
    """Bulk insert log entries for a given run."""
    rows = _prepare_rows(run_id, entries)
    if not rows:
        return 0
    stmt = insert(Log).values(rows)
    await session.execute(stmt)
    logger.debug("[db] inserted {} log rows for run_id={}", len(rows), run_id)
    return len(rows)


async def process_batch(session: AsyncSession, req: BatchRequest) -> int:
    """Process a batch of logs: upsert run, insert logs, commit."""
    logger.info(
        "[batch] run_id={} task_id={} action={} logs={}",
        req.run_id, req.task_id, req.action_name, len(req.logs),
    )
    try:
        update_task_data = "task_data" in req.model_fields_set
        await upsert_automation_run(
            session,
            run_id=req.run_id,
            task_id=req.task_id,
            profile_id=req.profile_id,
            action_name=req.action_name,
            task_data=req.task_data,
            update_task_data=update_task_data,
        )
        count = await insert_logs(session, req.run_id, req.logs)
        await session.commit()
        logger.info("[batch] stored run_id={} inserted={}", req.run_id, count)
        return count
    except Exception:
        logger.exception("[batch] failed run_id={}", req.run_id)
        await session.rollback()
        raise
