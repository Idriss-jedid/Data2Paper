from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db_schemes.schemes.base import Base

class Student_Task(Base):
    __tablename__ = "student_tasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    deadline = Column(DateTime, nullable=False)
    
    task = relationship("Task", back_populates="student_task")
    