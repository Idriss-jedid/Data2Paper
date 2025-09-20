"""
OAuth Routes for Google, GitHub, and Apple authentication
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import httpx
import jwt
from datetime import datetime, timedelta
import secrets

from database import get_db
from models.db_schemes.schemes.user import User
from schemas.user import UserCreate, UserResponse, Token
from auth import create_access_token, get_current_user

# Note: OAuth configuration will be loaded when dependencies are installed
try:
    from config_oauth import OAUTH_PROVIDERS
    OAUTH_ENABLED = True
except ImportError:
    OAUTH_PROVIDERS = {}
    OAUTH_ENABLED = False

router = APIRouter(prefix="/oauth", tags=["oauth"])

@router.get("/providers")
async def get_oauth_providers():
    """Get available OAuth providers"""
    if not OAUTH_ENABLED:
        return {"providers": [], "enabled": False, "message": "OAuth dependencies not installed"}
    
    return {
        "providers": [
            {
                "id": provider_id,
                "name": provider_data["name"],
                "icon": provider_data["icon"],
                "color": provider_data["color"]
            }
            for provider_id, provider_data in OAUTH_PROVIDERS.items()
        ],
        "enabled": True
    }

@router.get("/login/{provider}")
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth login with specified provider"""
    if not OAUTH_ENABLED:
        raise HTTPException(status_code=503, detail="OAuth not available - dependencies not installed")
    
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")
    
    # For now, return a simple redirect URL that the frontend can handle
    # This will be implemented once OAuth dependencies are installed
    return {
        "message": f"OAuth login with {provider} will be implemented once dependencies are installed",
        "provider": provider,
        "redirect_url": f"/oauth/callback/{provider}"
    }

@router.get("/callback/{provider}")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    """Handle OAuth callback and create/login user"""
    if not OAUTH_ENABLED:
        raise HTTPException(status_code=503, detail="OAuth not available - dependencies not installed")
    
    # This will be implemented once OAuth dependencies are installed
    return {
        "message": f"OAuth callback for {provider} will be implemented once dependencies are installed",
        "provider": provider
    }

# Helper function for manual OAuth user creation (for testing)
@router.post("/create-test-user/{provider}")
async def create_test_oauth_user(
    provider: str,
    user_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create a test OAuth user (for development purposes)"""
    if provider not in ['google', 'github', 'apple']:
        raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data['email']).first()
    
    if existing_user:
        # Update OAuth info
        setattr(existing_user, f'{provider}_id', user_data.get('id'))
        existing_user.is_oauth_user = True
        db.commit()
        db.refresh(existing_user)
        user = existing_user
    else:
        # Create new user
        user = User(
            name=user_data.get('name', user_data.get('email', '').split('@')[0]),
            email=user_data['email'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            username=user_data.get('username', user_data.get('email', '').split('@')[0]),
            avatar_url=user_data.get('avatar_url'),
            is_oauth_user=True,
            password_hash=None  # No password for OAuth users
        )
        
        setattr(user, f'{provider}_id', user_data.get('id'))
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/unlink/{provider}")
async def unlink_oauth_provider(
    provider: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlink OAuth provider from user account"""
    if provider not in ['google', 'github', 'apple']:
        raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")
    
    # Check if user has a password (if not, they can't unlink their only auth method)
    if not current_user.password_hash and getattr(current_user, f'{provider}_id'):
        # Count other linked providers
        other_providers = [p for p in ['google', 'github', 'apple'] if p != provider]
        has_other_auth = any(getattr(current_user, f'{p}_id') for p in other_providers)
        
        if not has_other_auth:
            raise HTTPException(
                status_code=400, 
                detail="Cannot unlink the only authentication method. Please set a password first."
            )
    
    # Remove provider ID
    setattr(current_user, f'{provider}_id', None)
    db.commit()
    
    provider_names = {'google': 'Google', 'github': 'GitHub', 'apple': 'Apple'}
    return {"message": f"{provider_names.get(provider, provider)} account unlinked successfully"}

@router.get("/linked")
async def get_linked_providers(current_user: User = Depends(get_current_user)):
    """Get list of linked OAuth providers for current user"""
    linked_providers = []
    provider_info = {
        'google': {'name': 'Google', 'icon': 'google'},
        'github': {'name': 'GitHub', 'icon': 'github'},
        'apple': {'name': 'Apple', 'icon': 'apple'}
    }
    
    for provider_id, provider_data in provider_info.items():
        if getattr(current_user, f'{provider_id}_id'):
            linked_providers.append({
                "id": provider_id,
                "name": provider_data["name"],
                "icon": provider_data["icon"]
            })
    
    return {"linked_providers": linked_providers}
