from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.model.user import user, CRUDUser
from schemas.user import User, UserCreate, UserUpdate
from auth import get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)]  # Protect all routes
)

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user.get_multi(db, skip=skip, limit=limit)
    # Convert SQLAlchemy models to Pydantic models
    return [
        User(
            id=u.id,
            username=u.name,
            email=u.email,
            full_name=u.name,
            role=u.role
        ) for u in users
    ]

@router.post("/", response_model=User)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    db_user = user.get_by_email(db, email=user_create.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create user data dictionary with correct field names
    # Map full_name from schema to name in database model
    user_data = {
        "name": user_create.full_name or user_create.username,
        "email": user_create.email,
        "password_hash": "default_password_hash",  # This should be properly hashed in a real application
        "role": user_create.role.value if user_create.role else "Student"  # Use the role from the request or default to Student
    }
    # Create a simple object with dict method for compatibility with CRUD base
    class UserDataObject:
        def dict(self):
            return user_data

    created_user = user.create(db, obj_in=UserDataObject())
    return User(
        id=created_user.id,
        username=created_user.name,
        email=created_user.email,
        full_name=created_user.name,
        role=created_user.role
    )

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(
        id=db_user.id,
        username=db_user.name,
        email=db_user.email,
        full_name=db_user.name,
        role=db_user.role
    )

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Convert Pydantic model to dict for CRUD operations
    update_data = {}
    if user_update.full_name is not None:
        update_data["name"] = user_update.full_name
    if user_update.username is not None:
        update_data["name"] = user_update.username
    if user_update.email is not None:
        update_data["email"] = user_update.email
    if user_update.role is not None:
        update_data["role"] = user_update.role.value
        
    # Create a simple object with dict method for compatibility with CRUD base
    class UserDataObject:
        def dict(self, **kwargs):
            return update_data

    updated_user = user.update(
        db, 
        db_obj=db_user, 
        obj_in=UserDataObject()
    )
    return User(
        id=updated_user.id,
        username=updated_user.name,
        email=updated_user.email,
        full_name=updated_user.name,
        role=updated_user.role
    )

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}