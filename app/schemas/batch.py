from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field
from app.schemas.enums import LogLevel


class LogEntry(BaseModel):
    timestamp: datetime
    level: LogLevel
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


class BatchRequest(BaseModel):
    run_id: str
    task_id: str
    profile_id: str
    action_name: str
    logs: List[LogEntry]
