from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AutomationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    task_id: str
    profile_id: str | None = None
    action_name: str
    status: str
    task_data: dict[str, Any] | None = None
    start_time: datetime
