from sqlalchemy.orm import Session
from typing import List, Optional
from ..db_schemes.schemes.user import User
from .base import CRUDBase

class CRUDUser(CRUDBase[User]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get a user by email"""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get a user by username"""
        return db.query(self.model).filter(self.model.username == username).first()

    def get_multi_by_role(self, db: Session, *, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users by role"""
        return db.query(self.model).filter(self.model.role == role).offset(skip).limit(limit).all()

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password"""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        # This is a placeholder - you would implement actual password verification here
        # using a library like passlib
        return plain_password == hashed_password

    def is_active(self, user: User) -> bool:
        """Check if a user is active"""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Check if a user is a superuser"""
        return user.is_superuser

# Create an instance of CRUDUser for direct use
user = CRUDUser(User)