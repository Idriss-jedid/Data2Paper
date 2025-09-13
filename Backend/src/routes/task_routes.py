from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.model.task import task, CRUDTask
from schemas.task import Task, TaskCreate, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.get("/", response_model=List[Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = task.get_multi(db, skip=skip, limit=limit)
    # Convert SQLAlchemy models to Pydantic models
    return [
        Task(
            id=t.id,
            title=t.title,
            description=t.description or "",
            status=str(t.status),
            user_id=t.user_id
        ) for t in tasks
    ]

@router.post("/", response_model=Task)
def create_task(task_create: TaskCreate, db: Session = Depends(get_db)):
    # Convert Pydantic model to dict for CRUD operations
    task_data = {
        "title": task_create.title,
        "description": task_create.description,
        "user_id": task_create.user_id,
        "status": "pending"
    }
    created_task = task.create(db, obj_in=type('obj', (object,), {'dict': lambda: task_data})())
    return Task(
        id=created_task.id,
        title=created_task.title,
        description=created_task.description or "",
        status=str(created_task.status),
        user_id=created_task.user_id
    )

@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = task.get(db, id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description or "",
        status=str(db_task.status),
        user_id=db_task.user_id
    )

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    db_task = task.get(db, id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # Convert Pydantic model to dict for CRUD operations
    update_data = {}
    if task_update.title is not None:
        update_data["title"] = task_update.title
    if task_update.description is not None:
        update_data["description"] = task_update.description
    if task_update.status is not None:
        update_data["status"] = task_update.status
        
    updated_task = task.update(
        db, 
        db_obj=db_task, 
        obj_in=type('obj', (object,), {'dict': lambda exclude_unset=True: update_data})()
    )
    return Task(
        id=updated_task.id,
        title=updated_task.title,
        description=updated_task.description or "",
        status=str(updated_task.status),
        user_id=updated_task.user_id
    )

@router.delete("/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = task.get(db, id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.remove(db, id=task_id)
    return {"message": "Task deleted successfully"}