from sqlalchemy.orm import Session
from typing import List, Optional
from ..db_schemes.schemes.task_status_history import Task_Status_History
from .base import CRUDBase

class CRUDTaskStatusHistory(CRUDBase[Task_Status_History]):
    def get_by_task_id(self, db: Session, *, task_id: int) -> List[Task_Status_History]:
        """Get task status history by task ID"""
        return db.query(self.model).filter(self.model.task_id == task_id).all()

    def get_by_task_and_status(self, db: Session, *, task_id: int, status: str) -> List[Task_Status_History]:
        """Get task status history by task ID and status"""
        return db.query(self.model).filter(
            self.model.task_id == task_id,
            self.model.status == status
        ).all()

# Create an instance of CRUDTaskStatusHistory for direct use
task_status_history = CRUDTaskStatusHistory(Task_Status_History)