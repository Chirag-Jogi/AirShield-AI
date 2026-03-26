"""
Database Models (Table Schemas)
Defines what data gets stored in the database.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from src.database.connection import Base


class AirQualityReading(Base):
    """
    Each row = one air quality reading for one city at one time.
    
    Example: Delhi's pollution data at 2:30 PM on March 23, 2026
    """
    __tablename__ = "air_quality_readings"

    # --- Primary Key ---
    id = Column(Integer, primary_key=True, autoincrement=True)

    # --- Location ---
    city = Column(String, nullable=False, index=True)  # index=True makes queries faster
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # --- Air Quality Index ---
    aqi = Column(Integer, nullable=True)  # 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor

    # --- Pollutants (μg/m³) ---
    co = Column(Float)     # Carbon Monoxide
    no = Column(Float)     # Nitrogen Monoxide
    no2 = Column(Float)    # Nitrogen Dioxide
    o3 = Column(Float)     # Ozone
    so2 = Column(Float)    # Sulphur Dioxide
    pm2_5 = Column(Float)  # Fine Particles (most dangerous!)
    pm10 = Column(Float)   # Coarse Particles
    nh3 = Column(Float)    # Ammonia

    # --- Timestamps ---
    measured_at = Column(DateTime, nullable=False)  # When the API measured it
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # When WE saved it

    # --- Data Source ---
    source = Column(String, default="openweathermap")  # Which API the data came from

    def __repr__(self):
        return f"<AirQuality {self.city} AQI={self.aqi} PM2.5={self.pm2_5} at {self.measured_at}>"
