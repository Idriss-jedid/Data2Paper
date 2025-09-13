from pydantic import BaseModel
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"

class TaskCreate(TaskBase):
    user_id: int

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True