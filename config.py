"""
AirShield AI — Central Configuration
Loads all settings from .env file.
Every module imports from here: from config import settings
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# This gives us the folder where config.py lives
BASE_DIR = Path(__file__).resolve().parent


     # --- Database ---
    DATABASE_URL: str = Field(
        default=f"sqlite:///{BASE_DIR / 'data' / 'airshield.db'}",
        description="SQLAlchemy-compatible database URL"
    )

    # --- API Credentials ---
    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Telegram Bot Token from @BotFather")
    OPENWEATHER_API_KEY: str = Field(default="", description="OpenWeatherMap API Key")
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API Key for LLM access")
    AQICN_API_KEY: str = ""

    # --- Cloud & Webhook Settings ---
    WEBHOOK_URL: str = Field(default="", description="Webhook URL for Render 24/7 reliability")
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")
    PORT: int = 10000


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

    @property
    def get_database_url(self) -> str:
        """Sanitizes the database URL for Supabase/PgBouncer compatibility."""
        url = str(self.DATABASE_URL)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql://", 1)
        return url


# --- This runs when any file imports config ---
settings = Settings()
settings.ensure_directories()