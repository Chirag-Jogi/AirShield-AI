"""
Database Query Functions — Async Edition
Updated for non-blocking I/O with AsyncSession.
All inputs are sanitized to 'Naive UTC' via to_naive_utc().
"""

from datetime import datetime
from sqlalchemy import select, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import AirQualityReading, User
from src.utils.logger import logger
from src.utils.time_utils import to_naive_utc

async def save_readings(session: AsyncSession, readings: list[dict]) -> int:
    """
    Save a list of air quality readings asynchronously.
    """
    saved = 0
    errors = 0

    for data in readings:
        try:
            # 1. Parse timestamp and ensure it is Naive UTC
            raw_ts = data["timestamp"]
            naive_ts = to_naive_utc(datetime.fromisoformat(raw_ts))
            
            reading = AirQualityReading(
                city=data["city"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                aqi=data["aqi"],
                co=data.get("co"),
                no=data.get("no"),
                no2=data.get("no2"),
                o3=data.get("o3"),
                so2=data.get("so2"),
                pm2_5=data.get("pm2_5"),
                pm10=data.get("pm10"),
                nh3=data.get("nh3"),
                measured_at=naive_ts,
                source=data.get("source", "openweathermap"),
                # created_at is handled by the model default
            )
            session.add(reading)
            await session.flush()  # validate this record immediately
            saved += 1
        except Exception as e:
            await session.rollback()
            errors += 1
            logger.error(f"❌ Failed to save record for {data.get('city', '?')}: {e}")

    await session.commit()
    logger.info(f"✅ Saved {saved} readings to database ({errors} errors)")
    return saved

async def get_latest_readings(session: AsyncSession, limit: int = 20) -> list:
    """Get the most recent readings across all cities."""
    stmt = select(AirQualityReading).order_by(desc(AirQualityReading.created_at)).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_city_readings(session: AsyncSession, city: str, limit: int = 100) -> list:
    """Get readings for a specific city."""
    stmt = (
        select(AirQualityReading)
        .filter(AirQualityReading.city == city)
        .order_by(desc(AirQualityReading.measured_at))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_city_status(session: AsyncSession, city: str):
    """Get the absolute latest reading for a city."""
    stmt = (
        select(AirQualityReading)
        .filter(AirQualityReading.city == city)
        .order_by(desc(AirQualityReading.measured_at))
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalars().first()

async def get_or_create_user(session: AsyncSession, telegram_id: int, first_name: str) -> User:
    """Check if user exists; if not, create them."""
    stmt = select(User).filter(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        user = User(telegram_id=telegram_id, first_name=first_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user

async def get_active_users(session: AsyncSession) -> list[User]:
    """Get all users who have alerts enabled."""
    stmt = select(User).filter(User.is_alert_enabled == True)
    result = await session.execute(stmt)
    return result.scalars().all()

async def update_user_city(session: AsyncSession, telegram_id: int, city_name: str):
    """Update a user's home city."""
    stmt = (
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(home_city=city_name)
    )
    await session.execute(stmt)
    await session.commit()

async def update_user_health(session: AsyncSession, telegram_id: int, profile: str):
    """Update a user's health profile."""
    stmt = (
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(health_profile=profile)
    )
    await session.execute(stmt)
    await session.commit()

async def update_user_last_morning(session: AsyncSession, telegram_id: int):
    """Mark that the user was sent their morning briefing today."""
    stmt = (
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(last_morning_at=to_naive_utc(datetime.utcnow()))
    )
    await session.execute(stmt)
    await session.commit()

async def update_user_last_alert(session: AsyncSession, telegram_id: int):
    """Mark that the user was sent an emergency alert just now."""
    stmt = (
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(last_alert_at=to_naive_utc(datetime.utcnow()))
    )
    await session.execute(stmt)
    await session.commit()

async def update_user_history(session: AsyncSession, telegram_id: int, history_json: str):
    """Save the persistent chat history to the cloud database."""
    stmt = (
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(chat_history=history_json)
    )
    await session.execute(stmt)
    await session.commit()
