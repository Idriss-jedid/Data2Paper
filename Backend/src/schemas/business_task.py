from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.enums.task_status import TaskStatus
from models.enums.priority import Priority


class BusinessTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_name: str
    due_date: datetime
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING


class BusinessTaskCreate(BusinessTaskBase):
    user_id: int
    initial_note: Optional[str] = "Business task created"


class BusinessTaskUpdate(BusinessTaskBase):
    pass


class BusinessTask(BusinessTaskBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True