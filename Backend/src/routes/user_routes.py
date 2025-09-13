from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.model.user import user, CRUDUser
from schemas.user import User, UserCreate, UserUpdate
from models.model.auth import get_current_active_user  # Fixed import

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user.get_multi(db, skip=skip, limit=limit)

    return [
        User(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            is_active=u.is_active
        ) for u in users
    ]

@router.post("/", response_model=User)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    db_user = user.get_by_email(db, email=user_create.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create user data dictionary with correct field names
    user_data = {
        "name": user_create.name,
        "email": user_create.email,
        "password_hash": user.get_password_hash(user_create.password),  # Properly hash the password
        "role": user_create.role.value if user_create.role else "User"  # Use the role from the request or default to User
    }
    # Create a simple object with dict method for compatibility with CRUD base
    class UserDataObject:
        def dict(self):
            return user_data

    created_user = user.create(db, obj_in=UserDataObject())
    return User(
        id=created_user.id,
        name=created_user.name,
        email=created_user.email,
        role=created_user.role,
        is_active=created_user.is_active
    )

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        role=db_user.role,
        is_active=db_user.is_active
    )

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = {}
    if user_update.name is not None:
        update_data["name"] = user_update.name
    if user_update.email is not None:
        update_data["email"] = user_update.email
    if user_update.password is not None:
        update_data["password_hash"] = user.get_password_hash(user_update.password)  # Hash password if provided
    if user_update.role is not None:
        update_data["role"] = user_update.role.value
        
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
        name=updated_user.name,
        email=updated_user.email,
        role=updated_user.role,
        is_active=updated_user.is_active
    )

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}