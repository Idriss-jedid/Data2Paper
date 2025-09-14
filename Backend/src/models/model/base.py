from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, List, Optional
from enum import Enum
from ..db_schemes.schemes.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in) -> ModelType:
        """Create a new record"""
        obj_data = obj_in.dict()
        # Handle enum values properly
        for key, value in obj_data.items():
            if isinstance(value, Enum):
                obj_data[key] = value.value
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in) -> ModelType:
        """Update an existing record"""
        obj_data = obj_in.dict(exclude_unset=True)
        # Handle enum values properly
        for key, value in obj_data.items():
            if isinstance(value, Enum):
                obj_data[key] = value.value
            setattr(db_obj, key, obj_data[key])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Remove a record by ID"""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj