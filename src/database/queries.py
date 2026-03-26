"""
Database Query Functions
Save and read air quality data from the database.
"""

from datetime import datetime
from sqlalchemy import desc
from src.database.connection import get_session
from src.database.models import AirQualityReading
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