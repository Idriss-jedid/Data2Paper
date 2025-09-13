from sqlalchemy.ext.declarative import declarative_base

# Both names point to the same declarative base for compatibility
SQLAlchemyBase = declarative_base()
Base = SQLAlchemyBase