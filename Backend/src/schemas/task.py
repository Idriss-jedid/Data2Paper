from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from models.enums.priority import Priority
from models.enums.task_status import TaskStatus

class TaskType(str, Enum):
    STUDENT = "student"
    BUSINESS = "business"
    EMPLOYMENT = "employment"
    CERTIFICATION = "certification"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING

class TaskCreate(TaskBase):
    user_id: int
    task_type: TaskType
    initial_note: Optional[str] = "Task created"  # Custom note for initial status history entry
    
    # Specialized fields for different task types
    subject: Optional[str] = None
    deadline: Optional[datetime] = None
    project_name: Optional[str] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    company: Optional[str] = None
    position: Optional[str] = None
    certification_name: Optional[str] = None
    issuer: Optional[str] = None
    expiry_date: Optional[datetime] = None

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True