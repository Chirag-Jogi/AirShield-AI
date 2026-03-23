"""
Database Connection Manager
Creates and manages the connection to the database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings
from src.utils.logger import logger


# --- Base class for all our database tables ---
class Base(DeclarativeBase):
    pass


# --- Create the database engine (the connection) ---
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set True to see SQL queries in terminal (useful for debugging)
)

# --- Session factory ---
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Get a database session. Always close it when done."""
    return SessionLocal()


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")