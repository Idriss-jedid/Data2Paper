from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.enums.task_status import TaskStatus

class TaskStatusHistoryBase(BaseModel):
    task_id: int
    status: TaskStatus
    note: Optional[str] = None

class TaskStatusHistoryCreate(TaskStatusHistoryBase):
    pass

class TaskStatusHistoryUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    note: Optional[str] = None

class TaskStatusHistory(TaskStatusHistoryBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True