from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Video & Audio RAG Chatbot"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://chatbot_user:changeme@db:5432/chatbot_db"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    # Chroma Vector DB
    CHROMA_URL: str = os.getenv("CHROMA_URL", "http://chroma:8000")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # File Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "5000"))  # MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    ALLOWED_EXTENSIONS: List[str] = [
        "mp4", "webm", "avi", "mov",  # Video
        "mp3", "wav", "m4a", "ogg"   # Audio
    ]

    # Processing
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    MIN_CHUNK_DURATION: int = int(os.getenv("MIN_CHUNK_DURATION", "30"))
    MAX_CHUNK_DURATION: int = int(os.getenv("MAX_CHUNK_DURATION", "300"))
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

    # RAG
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    SEARCH_TYPE: str = os.getenv("SEARCH_TYPE", "similarity")

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://frontend:3000",  # Docker internal
        "*"  # Allow all in development
    ]
    ALLOWED_HOSTS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
