from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

from ...enums.user_role import UserRole
from ...enums.user_status import UserStatus

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Allow null for OAuth users
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # OAuth fields
    is_oauth_user = Column(Boolean, default=False, nullable=False)
    google_id = Column(String(255), nullable=True, unique=True)
    github_id = Column(String(255), nullable=True, unique=True)
    apple_id = Column(String(255), nullable=True, unique=True)
    
    # Additional profile fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True, unique=True)
    avatar_url = Column(String(500), nullable=True)

    tasks = relationship("Task", back_populates="user")
    ai_reports = relationship("AI_Report", back_populates="user")

    @property
    def is_active(self) -> bool:
        """Check if user is active based on status"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.name or self.username or ""
    
    @property
    def is_superuser(self) -> bool:
        """Check if user is a superuser"""
        return self.role == UserRole.ADMIN