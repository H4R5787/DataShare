"""Application configuration settings for Secure Pass RxQ."""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "Secure Pass RxQ"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./secure_pass.db"
    )
    
    # Security & Tokens
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "dev-insecure-secret-key-change-in-production-rxq-991823"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for dev convenience
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OTP Configuration
    OTP_EXPIRE_SECONDS: int = 300  # 5 minutes
    MOCK_OTP_DEFAULT: str = "123456"
    ENABLE_MOCK_OTP: bool = True
    
    # Telecom & Payment Mock Settings
    TELECOM_MODE: str = os.getenv("TELECOM_MODE", "mock")  # mock | live
    PAYMENT_MODE: str = os.getenv("PAYMENT_MODE", "mock")  # mock | live
    MOCK_SIMULATE_LATENCY_MS: int = 200
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]


settings = Settings()
