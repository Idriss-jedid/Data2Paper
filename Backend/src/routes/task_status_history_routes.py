from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.model.task_status_history import task_status_history
from schemas.task_status_history import TaskStatusHistory, TaskStatusHistoryCreate, TaskStatusHistoryUpdate
from models.model.auth import get_current_active_user
from models.db_schemes.schemes.task_status_history import Task_Status_History
from models.enums.task_status import TaskStatus

router = APIRouter(
    prefix="/task-status-history",
    tags=["task-status-history"],
    dependencies=[Depends(get_current_active_user)]  # Protect all routes
)

@router.get("/task/{task_id}", response_model=List[TaskStatusHistory])
def read_task_status_history(task_id: int, db: Session = Depends(get_db)):
    """Get all status history entries for a specific task"""
    history = task_status_history.get_by_task_id(db, task_id=task_id)
    return [
        TaskStatusHistory(
            id=h.id,
            task_id=h.task_id,
            status=h.status,
            updated_at=h.updated_at,
            note=h.note
        ) for h in history
    ]

@router.post("/", response_model=TaskStatusHistory)
def create_task_status_history(history_create: TaskStatusHistoryCreate, db: Session = Depends(get_db)):
    """Create a new task status history entry"""
    # Verify that the task exists
    from models.model.task import task
    db_task = task.get(db, id=history_create.task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update the task status if provided
    if history_create.status:
        from models.model.base import CRUDBase
        from models.db_schemes.schemes.task import Task as TaskModel
        task_crud = CRUDBase(TaskModel)
        
        class TaskUpdateObject:
            def dict(self, exclude_unset=True):
                return {"status": history_create.status}
        
        task_crud.update(db, db_obj=db_task, obj_in=TaskUpdateObject())
    
    # Create the history entry
    db_history = Task_Status_History(**history_create.dict())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return TaskStatusHistory(
        id=db_history.id,
        task_id=db_history.task_id,
        status=db_history.status,
        updated_at=db_history.updated_at,
        note=db_history.note
    )

@router.put("/{history_id}", response_model=TaskStatusHistory)
def update_task_status_history(history_id: int, history_update: TaskStatusHistoryUpdate, db: Session = Depends(get_db)):
    """Update a task status history entry"""
    db_history = task_status_history.get(db, id=history_id)
    if db_history is None:
        raise HTTPException(status_code=404, detail="Task status history entry not found")
    
    # Update the task status if provided
    if history_update.status:
        from models.model.task import task
        db_task = task.get(db, id=db_history.task_id)
        if db_task:
            from models.model.base import CRUDBase
            from models.db_schemes.schemes.task import Task as TaskModel
            task_crud = CRUDBase(TaskModel)
            
            class TaskUpdateObject:
                def dict(self, exclude_unset=True):
                    return {"status": history_update.status}
            
            task_crud.update(db, db_obj=db_task, obj_in=TaskUpdateObject())
    
    # Update fields that are provided
    update_data = history_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_history, field, value)
    
    db.commit()
    db.refresh(db_history)
    
    return TaskStatusHistory(
        id=db_history.id,
        task_id=db_history.task_id,
        status=db_history.status,
        updated_at=db_history.updated_at,
        note=db_history.note
    )

@router.delete("/{history_id}", response_model=dict)
def delete_task_status_history(history_id: int, db: Session = Depends(get_db)):
    """Delete a task status history entry"""
    db_history = task_status_history.get(db, id=history_id)
    if db_history is None:
        raise HTTPException(status_code=404, detail="Task status history entry not found")
    
    db.delete(db_history)
    db.commit()
    
    return {"message": "Task status history entry deleted successfully"}