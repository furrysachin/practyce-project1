"""
Application configuration - database URL and settings.
Uses environment variables with defaults for local development.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # SQLite fallback since PostgreSQL is not installed
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./retail_banking.db"
    )

    # API
    API_PREFIX: str = "/api"
    MAX_UPLOAD_SIZE_MB: int = 100

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
