from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models.model.user import user as crud_user
from schemas.user import User, UserCreate, Token, UserLogin
from models.model.auth import authenticate_user, create_access_token, get_password_hash, get_current_active_user
from config import settings

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/register", response_model=User)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = crud_user.get_by_email(db, email=user_create.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_create.password)
    
    # Create user data object with proper structure
    class UserData:
        def dict(self, **kwargs):
            user_data = {
                "name": user_create.name,
                "email": user_create.email,
                "password_hash": hashed_password
            }
            # Add role if provided, otherwise use default
            if user_create.role:
                user_data["role"] = user_create.role.value
            else:
                user_data["role"] = "User"  # Default role value
            return user_data
    
    # Create the user
    db_user = crud_user.create(db=db, obj_in=UserData())
    
    return User(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        role=db_user.role,
        is_active=db_user.is_active
    )

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token (OAuth2 compatible)"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-simple", response_model=Token)
def login_user_simple(user_login: UserLogin, db: Session = Depends(get_db)):
    """Simple login with JSON body - easier to use in Swagger UI"""
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
def read_users_me(current_user = Depends(get_current_active_user)):
    """Get current user information"""
    return User(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )

@router.post("/refresh", response_model=Token)
def refresh_token(current_user = Depends(get_current_active_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
