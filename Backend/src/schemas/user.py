from pydantic import BaseModel, EmailStr
from typing import Optional
from models.enums.user_role import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: Optional[str] = None  # Allow None for OAuth users
    role: Optional[UserRole] = UserRole.USER
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_oauth_user: Optional[bool] = False

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: Optional[UserRole] = None
    is_active: bool = True
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_oauth_user: bool = False
    full_name: Optional[str] = None

    class Config:
        from_attributes = True

class User(UserResponse):
    """Alias for backward compatibility"""
    pass

class UserInDB(User):
    password_hash: Optional[str] = None
    google_id: Optional[str] = None
    github_id: Optional[str] = None
    apple_id: Optional[str] = None

# OAuth-specific schemas
class OAuthUser(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_id: str
    provider: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None

class TokenData(BaseModel):
    email: Optional[str] = None