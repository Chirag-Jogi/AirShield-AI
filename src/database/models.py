"""
Database Models (Table Schemas)
Defines what data gets stored in the database.
All DateTimes are standardized to UTC-Naive for PostgreSQL-Asyncpg consistency.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, BigInteger
from src.database.connection import Base

class AirQualityReading(Base):
    """
    Each row = one air quality reading for one city at one time.
    """
    __tablename__ = "air_quality_readings"

    # --- Primary Key ---
    id = Column(Integer, primary_key=True, autoincrement=True)

    # --- Location ---
    city = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # --- Air Quality Index ---
    aqi = Column(Integer, nullable=True)

    # --- Pollutants (μg/m³) ---
    co = Column(Float)
    no = Column(Float)
    no2 = Column(Float)
    o3 = Column(Float)
    so2 = Column(Float)
    pm2_5 = Column(Float)
    pm10 = Column(Float)
    nh3 = Column(Float)

    # --- Timestamps (Naive UTC) ---
    measured_at = Column(DateTime(timezone=False), nullable=False)
    created_at = Column(DateTime(timezone=False), default=datetime.utcnow)

    # --- Data Source ---
    source = Column(String, default="openweathermap")

    def __repr__(self):
        return f"<AirQuality {self.city} AQI={self.aqi} PM2.5={self.pm2_5} at {self.measured_at}>"

class User(Base):
    """
    Stores permanent user profiles and preferences.
    """
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True)
    first_name = Column(String)
    home_city = Column(String, nullable=True)
    health_profile = Column(String, default="None")
    is_alert_enabled = Column(Boolean, default=True)
    
    # --- Timestamps (Naive UTC) ---
    last_morning_at = Column(DateTime(timezone=False), nullable=True)
    last_alert_at = Column(DateTime(timezone=False), nullable=True)
    chat_history = Column(String, default="[]")
    created_at = Column(DateTime(timezone=False), default=datetime.utcnow)
    last_active = Column(DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow)
