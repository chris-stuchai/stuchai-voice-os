"""
Shared configuration module.

Loads environment variables and provides application settings.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/stuchai_voice_os"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "stuchai_voice_os"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = True
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    LM_STUDIO_URL: str = "http://localhost:1234/v1"
    LLM_MODEL: str = "gpt-4o"  # Updated to latest model
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    
    # Voice Services
    ASR_PROVIDER: str = "whisper"
    WHISPER_MODEL: str = "base"
    TTS_PROVIDER: str = "coqui"
    COQUI_TTS_URL: str = "http://localhost:5002"
    COQUI_VOICE_MODEL: str = "default"
    
    # MCP
    MCP_SERVER_URL: str = "http://localhost:3001"
    MCP_ENABLED: bool = True
    
    # WebSocket/WebRTC
    WS_PORT: int = 8001
    WEBRTC_ENABLED: bool = False
    
    # Application
    APP_NAME: str = "Stuchai Voice OS"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # Admin
    DEFAULT_ADMIN_EMAIL: str = "admin@stuchai.com"
    DEFAULT_ADMIN_PASSWORD: str = "ChangeMe123!"
    
    # Railway
    RAILWAY_ENVIRONMENT: Optional[str] = None
    RAILWAY_PROJECT_ID: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Voice Dataset
    VOICE_DATASET_PATH: str = "./voice_datasets"
    MAX_VOICE_SAMPLE_SIZE_MB: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

