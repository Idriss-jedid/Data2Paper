from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.enums.task_status import TaskStatus


class StudentTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    deadline: datetime
    status: TaskStatus = TaskStatus.PENDING


class StudentTaskCreate(StudentTaskBase):
    user_id: int
    initial_note: Optional[str] = "Student task created"


class StudentTaskUpdate(StudentTaskBase):
    pass


class StudentTask(StudentTaskBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True