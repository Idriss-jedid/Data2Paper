"""
Enums for LLM providers
"""
from enum import Enum

class DocumentTypeEnum(str, Enum):
    DOCUMENT = "document"
    QUERY = "query"

class GeminiEnums(str, Enum):
    USER = "user"
    MODEL = "model"
    DOCUMENT = "document"
    QUERY = "query"