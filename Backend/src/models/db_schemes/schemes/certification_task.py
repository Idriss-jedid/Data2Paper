
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Certification_Task(Base):
    __tablename__ = "certification_tasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    certification_name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    
    task = relationship("Task", back_populates="certification_task")
