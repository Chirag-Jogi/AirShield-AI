"""
AirShield AI — Elite Configuration System
Powered by Pydantic V2 for robust validation and secret management.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, validator

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    Elite Settings Management.
    Automatically loads from .env and environment variables.
    """

    # --- Project Metadata ---
    PROJECT_NAME: str = "AirShield AI"
    PROJECT_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")

    # --- API Credentials (Required for Production) ---
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot Token from @BotFather")
    OPENWEATHER_API_KEY: str = Field(..., description="OpenWeatherMap API Key")
    OPENROUTER_API_KEY: str = Field(..., description="OpenRouter API Key for LLM access")
    AQICN_API_KEY: Optional[str] = None

    # --- Database Configuration ---
    # Default to a local SQLite database if DATABASE_URL is not provided
    DATABASE_URL: str = Field(
        default=f"sqlite:///{BASE_DIR / 'data' / 'airshield.db'}",
        description="SQLAlchemy-compatible database URL"
    )

    # --- API Optimization ---
    API_MAX_RETRIES: int = 3
    API_RETRY_DELAY: float = 2.0  # Base delay for exponential backoff
    CONNECT_TIMEOUT: float = 30.0
    READ_TIMEOUT: float = 30.0

    # --- Persistence Paths ---
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    MODELS_DIR: Path = BASE_DIR / "data" / "models"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def ensure_directories(self):
        """Auto-provision necessary directories for the system."""
        for dir_path in [self.DATA_DIR, self.LOGS_DIR, self.MODELS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

# Instantiate as a singleton
settings = Settings()
settings.ensure_directories()
