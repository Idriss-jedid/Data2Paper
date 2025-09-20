from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    # Database Settings
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    # Email Settings (optional)
    smtp_server: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    mail_from: Optional[str] = None
    mail_from_name: Optional[str] = "Data2Paper"
    
    # JWT Settings
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # LLM Settings
    gemini_api_key: Optional[str] = None 
    
    # OAuth Settings
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    apple_client_id: Optional[str] = None
    apple_client_secret: Optional[str] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    
    # Application URLs
    frontend_url: str = "http://localhost:4200"
    backend_url: str = "http://localhost:8000"
    
    # File Storage
    upload_directory: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.database_username}:{self.database_password}@{self.database_hostname}:{self.database_port}/{self.database_name}"

settings = Settings()