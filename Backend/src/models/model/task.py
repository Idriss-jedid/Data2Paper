from sqlalchemy.orm import Session
from typing import List, Optional
from ..db_schemes.schemes.task import Task
from .base import CRUDBase

class CRUDTask(CRUDBase[Task]):
    def get_multi_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get multiple tasks by user ID"""
        return db.query(self.model).filter(self.model.user_id == user_id).offset(skip).limit(limit).all()

    def get_multi_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get multiple tasks by status"""
        return db.query(self.model).filter(self.model.status == status).offset(skip).limit(limit).all()

    def get_multi_by_priority(self, db: Session, *, priority: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get multiple tasks by priority"""
        return db.query(self.model).filter(self.model.priority == priority).offset(skip).limit(limit).all()

    def get_overdue_tasks(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get overdue tasks"""
        from datetime import datetime
        return db.query(self.model).filter(
            self.model.due_date < datetime.utcnow(),
            self.model.status != 'completed'
        ).offset(skip).limit(limit).all()

# Create an instance of CRUDTask for direct use
task = CRUDTask(Task)