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
    Returns how many were saved successfully.
    """
    session = get_session()
    saved = 0
    try:
        for data in readings:
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
            saved += 1
        session.commit()  # Save all at once
        logger.info(f"✅ Saved {saved} readings to database")
    except Exception as e:
        session.rollback()  # Undo everything if error
        logger.error(f"❌ Failed to save readings: {e}")
    finally:
        session.close()  # Always close the session
    return saved
def get_latest_readings() -> list:
    """Get the most recent reading for each city."""
    session = get_session()
    try:
        results = (
            session.query(AirQualityReading)
            .order_by(desc(AirQualityReading.created_at))
            .limit(10)
            .all()
        )
        return results
    finally:
        session.close()
def get_city_readings(city: str, limit: int = 100) -> list:
    """Get readings for a specific city."""
    session = get_session()
    try:
        results = (
            session.query(AirQualityReading)
            .filter(AirQualityReading.city == city)
            .order_by(desc(AirQualityReading.measured_at))
            .limit(limit)
            .all()
        )
        return results
    finally:
        session.close()