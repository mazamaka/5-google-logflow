from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

from app.schemas.enums import LogLevel


class LogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: int
    run_id: str
    timestamp: datetime
    level: LogLevel
    message: str | None = None
    data: Dict[str, Any]
