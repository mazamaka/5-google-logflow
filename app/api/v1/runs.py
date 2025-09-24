from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models.automation_run import AutomationRun
from app.schemas.automation_run import AutomationRunRead
from app.models.log import Log
from app.schemas.log_read import LogRead
from app.schemas.enums import LogLevel
from app.core.logging_config import logger

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("", response_model=list[AutomationRunRead])
async def list_runs(
    task_id: str | None = Query(default=None),
    profile_id: str | None = Query(default=None),
    action_name: str | None = Query(default=None),
    status: str | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> list[AutomationRunRead]:
    logger.info(
        f"[api] GET /api/v1/runs task_id={task_id} profile_id={profile_id} action_name={action_name} status={status}"
    )
    stmt: Select[tuple[AutomationRun]] = select(AutomationRun)

    conditions = []
    if task_id is not None:
        conditions.append(AutomationRun.task_id == task_id)
    if profile_id is not None:
        conditions.append(AutomationRun.profile_id == profile_id)
    if action_name is not None:
        conditions.append(AutomationRun.action_name == action_name)
    if status is not None:
        conditions.append(AutomationRun.status == status)
    if start_time is not None:
        conditions.append(AutomationRun.start_time >= start_time)
    if end_time is not None:
        conditions.append(AutomationRun.start_time <= end_time)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.order_by(AutomationRun.start_time.desc()).offset(offset).limit(limit)

    result = await session.execute(stmt)
    rows = result.scalars().all()
    logger.debug(f"[api] /runs -> {len(rows)} items")
    return rows


@router.get("/{run_id}", response_model=AutomationRunRead)
async def get_run(run_id: str, session: AsyncSession = Depends(get_db_session)) -> AutomationRunRead:
    logger.info(f"[api] GET /api/v1/runs/{run_id}")
    obj = await session.get(AutomationRun, run_id)
    if not obj:
        logger.warning(f"[api] run not found run_id={run_id}")
        raise HTTPException(status_code=404, detail="Запуск не найден")
    return obj


@router.get("/{run_id}/logs", response_model=list[LogRead])
async def get_run_logs(
    run_id: str,
    level: LogLevel | None = Query(default=None, description="Фильтр по уровню"),
    start_time: datetime | None = Query(default=None, description="Начало интервала (ISO8601)"),
    end_time: datetime | None = Query(default=None, description="Конец интервала (ISO8601)"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> list[LogRead]:
    logger.info(
        f"[api] GET /api/v1/runs/{run_id}/logs level={level} start_time={start_time} end_time={end_time} limit={limit} offset={offset}"
    )
    stmt: Select[tuple[Log]] = select(Log).where(Log.run_id == run_id)
    if level is not None:
        stmt = stmt.where(Log.level == level.value)
    if start_time is not None:
        stmt = stmt.where(Log.timestamp >= start_time)
    if end_time is not None:
        stmt = stmt.where(Log.timestamp <= end_time)
    stmt = stmt.order_by(Log.timestamp.asc()).offset(offset).limit(limit)

    result = await session.execute(stmt)
    rows = result.scalars().all()
    logger.debug(f"[api] /runs/{run_id}/logs -> {len(rows)} items")
    return rows
