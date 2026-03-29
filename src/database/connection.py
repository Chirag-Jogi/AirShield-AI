"""
Elite Database Connection Manager — Async Edition
Transitioned to Async SQLAlchemy for non-blocking I/O.
Optimized for Supabase/PgBouncer with 'Giga-Sledgehammer' Pool Fix.
"""

from typing import AsyncGenerator
import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import settings
from src.utils.logger import logger

# --- Base class for all our database tables ---
class Base(DeclarativeBase):
    pass

# --- Create the Async Database Engine ---
# 1. Start with the raw URL from settings
db_url = settings.DATABASE_URL

# 2. Map legacy protocols to async-compatible ones
if db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif "postgres" in db_url:
    # Ensure correct driver prefix
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://")
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # 3. Giga-Sledgehammer: Append the cache-disable parameter to the URL itself
    if "?" in db_url:
        db_url += "&prepared_statement_cache_size=0"
    else:
        db_url += "?prepared_statement_cache_size=0"

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    # 4. Giga-Sledgehammer: Force-Disable caching at the driver connection level too
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    }
)

# --- Async Session factory ---
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Create all tables in the database asynchronously."""
    async with engine.begin() as conn:
        from src.database.models import User, AirQualityReading
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Elite Database tables synchronized (Async).")