from __future__ import annotations

from datetime import timezone
from typing import Iterable

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

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
) -> None:
    stmt = (
        pg_insert(AutomationRun)
        .values(
            run_id=run_id,
            task_id=task_id,
            profile_id=profile_id,
            action_name=action_name,
        )
        .on_conflict_do_update(
            index_elements=[AutomationRun.run_id],
            set_={
                "task_id": task_id,
                "profile_id": profile_id,
                "action_name": action_name,
            },
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
    rows = _prepare_rows(run_id, entries)
    if not rows:
        return 0
    stmt = insert(Log).values(rows)
    await session.execute(stmt)
    return len(rows)


async def process_batch(session: AsyncSession, req: BatchRequest) -> int:
    await upsert_automation_run(
        session,
        run_id=req.run_id,
        task_id=req.task_id,
        profile_id=req.profile_id,
        action_name=req.action_name,
    )
    count = await insert_logs(session, req.run_id, req.logs)
    await session.commit()
    return count
