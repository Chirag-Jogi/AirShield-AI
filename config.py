"""
AirShield AI — Central Configuration
Loads all settings from .env file.
Every module imports from here: from config import settings
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# This gives us the folder where config.py lives
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """All app settings. Loaded automatically from .env file."""

    # --- Project Info ---
    PROJECT_NAME: str = "AirShield AI"
    PROJECT_VERSION: str = "0.1.0"
    APP_ENV: str = "development"

    # --- API Keys (empty default = won't crash if missing) ---
    OPENWEATHER_API_KEY: str = ""
    AQICN_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # --- App Settings ---
    LOG_LEVEL: str = "INFO"

    # --- Paths ---
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    MODELS_DIR: Path = BASE_DIR / "data" / "models"

    # This tells pydantic WHERE to find the .env file
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def ensure_directories(self):
        """Create data folders if they don't exist."""
        for dir_path in [self.DATA_DIR, self.RAW_DATA_DIR,
                         self.PROCESSED_DATA_DIR, self.MODELS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


# --- This runs when any file imports config ---
settings = Settings()
settings.ensure_directories()