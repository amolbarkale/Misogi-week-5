from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database settings
    database_url: str = "sqlite:///./data/documents.db"
    
    # File storage settings
    uploads_directory: str = "./data/uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = ["pdf", "txt", "md", "doc", "docx"]
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # LLM settings (for future use)
    openai_api_key: Optional[str] = None
    
    # Vector database settings (for future use)
    qdrant_url: str = "http://localhost:6333"
    
    class Config:
        env_file = ".env"

# Create global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.uploads_directory, exist_ok=True) 