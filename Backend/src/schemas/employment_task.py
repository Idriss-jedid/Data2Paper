from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.enums.task_status import TaskStatus


class EmploymentTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    company: str
    position: str
    deadline: datetime
    status: TaskStatus = TaskStatus.PENDING


class EmploymentTaskCreate(EmploymentTaskBase):
    user_id: int
    initial_note: Optional[str] = "Employment task created"


class EmploymentTaskUpdate(EmploymentTaskBase):
    pass


class EmploymentTask(EmploymentTaskBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True