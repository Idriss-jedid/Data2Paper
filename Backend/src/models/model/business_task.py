
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db_schemes.schemes.base import Base
from models.enums.priority import Priority

class Business_Task(Base):
    __tablename__ = "business_tasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    project_name = Column(String(255), nullable=False)
    priority = Column(Enum(Priority), nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    task = relationship("Task", back_populates="business_task")
