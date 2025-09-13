
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from db_schemes.schemes.base import Base
from models.enums.task_status import TaskStatus

# Import for type hints
from typing import Optional

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="tasks")
    status_history = relationship("Task_Status_History", back_populates="task")
    student_task = relationship("Student_Task", back_populates="task", uselist=False)
    business_task = relationship("Business_Task", back_populates="task", uselist=False)
    employment_task = relationship("Employment_Task", back_populates="task", uselist=False)
    certification_task = relationship("Certification_Task", back_populates="task", uselist=False)
