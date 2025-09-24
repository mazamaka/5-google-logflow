from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LogCreate(BaseModel):
    level: LogLevel
    message: str
    source: str | None = None
    context: dict[str, Any] | None = None


class LogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    level: LogLevel
    message: str
    source: str | None = None
    context: dict[str, Any] | None = None
    minio_object_key: str | None = Field(default=None)
