from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.enums.task_status import TaskStatus


class CertificationTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    certification_name: str
    issuer: str
    expiry_date: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING


class CertificationTaskCreate(CertificationTaskBase):
    user_id: int
    initial_note: Optional[str] = "Certification task created"


class CertificationTaskUpdate(CertificationTaskBase):
    pass


class CertificationTask(CertificationTaskBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True