from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.model.task import task, CRUDTask
from schemas.task import Task, TaskCreate, TaskUpdate, TaskType
from models.model.auth import get_current_active_user  # Fixed import
from models.db_schemes.schemes.task import Task as TaskModel
from models.db_schemes.schemes.student_task import Student_Task
from models.db_schemes.schemes.business_task import Business_Task
from models.db_schemes.schemes.employment_task import Employment_Task
from models.db_schemes.schemes.certification_task import Certification_Task
from models.db_schemes.schemes.task_status_history import Task_Status_History
from models.enums.task_status import TaskStatus
from models.enums.priority import Priority

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_current_active_user)]  # Protect all routes
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
            status=t.status,
            user_id=t.user_id
        ) for t in tasks
    ]

@router.post("/", response_model=Task)
def create_task(task_create: TaskCreate, db: Session = Depends(get_db)):
    # Create the base task
    task_data = {
        "title": task_create.title,
        "description": task_create.description,
        "user_id": task_create.user_id,
        "status": TaskStatus.PENDING  # Use the enum value directly
    }
    
    # Create a proper object with dict method
    class TaskDataObject:
        def dict(self):
            return task_data
    
    created_task = task.create(db, obj_in=TaskDataObject())
    
    # Create specialized task based on task type
    if task_create.task_type == TaskType.STUDENT:
        if not task_create.subject or not task_create.deadline:
            raise HTTPException(status_code=400, detail="Student tasks require subject and deadline")
        student_task_data = {
            "task_id": created_task.id,
            "subject": task_create.subject,
            "deadline": task_create.deadline
        }
        student_task = Student_Task(**student_task_data)
        db.add(student_task)
    
    elif task_create.task_type == TaskType.BUSINESS:
        if not task_create.project_name or not task_create.due_date:
            raise HTTPException(status_code=400, detail="Business tasks require project_name and due_date")
        business_task_data = {
            "task_id": created_task.id,
            "project_name": task_create.project_name,
            "priority": task_create.priority or Priority.MEDIUM,
            "due_date": task_create.due_date
        }
        business_task = Business_Task(**business_task_data)
        db.add(business_task)
    
    elif task_create.task_type == TaskType.EMPLOYMENT:
        if not task_create.company or not task_create.position or not task_create.deadline:
            raise HTTPException(status_code=400, detail="Employment tasks require company, position and deadline")
        employment_task_data = {
            "task_id": created_task.id,
            "company": task_create.company,
            "position": task_create.position,
            "deadline": task_create.deadline
        }
        employment_task = Employment_Task(**employment_task_data)
        db.add(employment_task)
    
    elif task_create.task_type == TaskType.CERTIFICATION:
        if not task_create.certification_name or not task_create.issuer:
            raise HTTPException(status_code=400, detail="Certification tasks require certification_name and issuer")
        certification_task_data = {
            "task_id": created_task.id,
            "certification_name": task_create.certification_name,
            "issuer": task_create.issuer,
            "expiry_date": task_create.expiry_date
        }
        certification_task = Certification_Task(**certification_task_data)
        db.add(certification_task)
    
    # Create initial task status history entry
    status_history_data = {
        "task_id": created_task.id,
        "status": TaskStatus.PENDING,
        "note": task_create.initial_note  # Use custom note
    }
    status_history = Task_Status_History(**status_history_data)
    db.add(status_history)
    
    # Commit all changes
    db.commit()
    db.refresh(created_task)
    
    return Task(
        id=created_task.id,
        title=created_task.title,
        description=created_task.description or "",
        status=created_task.status,
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
        status=db_task.status,
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
    
    # Create a proper object with dict method
    class UpdateDataObject:
        def dict(self, exclude_unset=True):
            return update_data
        
    updated_task = task.update(
        db, 
        db_obj=db_task, 
        obj_in=UpdateDataObject()
    )
    return Task(
        id=updated_task.id,
        title=updated_task.title,
        description=updated_task.description or "",
        status=updated_task.status,
        user_id=updated_task.user_id
    )

@router.delete("/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = task.get(db, id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.remove(db, id=task_id)
    return {"message": "Task deleted successfully"}