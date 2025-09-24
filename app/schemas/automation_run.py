from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AutomationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    task_id: str
    profile_id: str | None = None
    action_name: str
    status: str
    start_time: datetime
