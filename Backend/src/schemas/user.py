from pydantic import BaseModel
from typing import Optional
from models.enums.user_role import UserRole

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    role: Optional[UserRole] = UserRole.STUDENT

class UserUpdate(UserBase):
    role: Optional[UserRole] = None

class User(UserBase):
    id: int
    role: Optional[UserRole] = None

    class Config:
        from_attributes = True