
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db_schemes.schemes.base import Base
from models.enums.task_status import TaskStatus

class Task_Status_History(Base):
    __tablename__ = "task_status_history"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    status = Column(Enum(TaskStatus), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    note = Column(Text)

    task = relationship("Task", back_populates="status_history")
