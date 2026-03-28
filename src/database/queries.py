"""
Database Query Functions
Save and read air quality data from the database.
"""

from datetime import datetime
from sqlalchemy import desc
from src.database.connection import get_session
from src.database.models import AirQualityReading
from src.database.models import User
from src.utils.logger import logger


def save_readings(readings: list[dict]) -> int:
    """
    Save a list of air quality readings to the database.
    Saves each record individually — a single bad record does NOT
    roll back the entire batch.
    Returns number of successfully saved records.
    """
    session = get_session()
    saved = 0
    errors = 0

    try:
        for data in readings:
            try:
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
                    measured_at=datetime.fromisoformat(data["timestamp"]),
                    source=data.get("source", "openweathermap"),
                )
                session.add(reading)
                session.flush()  # validate this record immediately
                saved += 1
            except Exception as e:
                session.rollback()
                errors += 1
                logger.error(
                    f"❌ Failed to save record for {data.get('city', '?')}: {e}"
                )

        session.commit()
        logger.info(f"✅ Saved {saved} readings to database ({errors} errors)")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Batch commit failed: {e}")

    finally:
        session.close()

    return saved


def get_latest_readings(limit: int = 20) -> list:
    """Get the most recent readings across all cities."""
    session = get_session()
    try:
        return (
            session.query(AirQualityReading)
            .order_by(desc(AirQualityReading.created_at))
            .limit(limit)
            .all()
        )
    finally:
        session.close()


def get_city_readings(city: str, limit: int = 100) -> list:
    """Get readings for a specific city."""
    session = get_session()
    try:
        return (
            session.query(AirQualityReading)
            .filter(AirQualityReading.city == city)
            .order_by(desc(AirQualityReading.measured_at))
            .limit(limit)
            .all()
        )
    finally:
        session.close()


def get_city_status(city: str):
    """Get the absolute latest reading for a city."""
    session = get_session()
    try:
        return (
            session.query(AirQualityReading)
            .filter(AirQualityReading.city == city)
            .order_by(desc(AirQualityReading.measured_at))
            .first()
        )
    finally:
        session.close()




def get_or_create_user(telegram_id: int, first_name: str) -> User:
    """Check if user exists; if not, create them."""
    session = get_session()
    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, first_name=first_name)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    finally:
        session.close()


def get_active_users() -> list[User]:
    """Get all users who have alerts enabled."""
    session = get_session()
    try:
        return session.query(User).filter(User.is_alert_enabled == True).all()
    finally:
        session.close()

def update_user_city(telegram_id: int, city_name: str):
    """Update a user's home city."""
    session = get_session()
    try:
        session.query(User).filter(User.telegram_id == telegram_id).update({"home_city": city_name})
        session.commit()
    finally:
        session.close()

def update_user_health(telegram_id: int, profile: str):
    """Update a user's health profile."""
    session = get_session()
    try:
        session.query(User).filter(User.telegram_id == telegram_id).update({"health_profile": profile})
        session.commit()
    finally:
        session.close()


def update_user_last_morning(telegram_id: int):
    """Mark that the user was sent their morning briefing today."""
    session = get_session()
    try:
        session.query(User).filter(User.telegram_id == telegram_id).update({"last_morning_at": datetime.utcnow()})
        session.commit()
    finally:
        session.close()


def update_user_last_alert(telegram_id: int):
    """Mark that the user was sent an emergency alert just now."""
    session = get_session()
    try:
        session.query(User).filter(User.telegram_id == telegram_id).update({"last_alert_at": datetime.utcnow()})
        session.commit()
    finally:
        session.close()
