"""
Historical Data Loader
Loads cleaned city_hour_clean.csv into the SQLite database.

What it does:
1. Reads cleaned CSV from data/processed/
2. Maps CSV column names to database column names
3. Looks up latitude/longitude from cities config
4. Inserts rows in batches (fast) into AirQualityReading table
"""

import pandas as pd
from datetime import datetime

from config import settings
from src.data.cities import INDIAN_CITIES
from src.database.connection import get_session, init_db
from src.database.models import AirQualityReading
from src.utils.logger import logger


# Map CSV column names → database column names
COLUMN_MAP = {
    "City": "city",
    "Datetime": "measured_at",
    "PM2.5": "pm2_5",
    "PM10": "pm10",
    "NO": "no",
    "NO2": "no2",
    "NH3": "nh3",
    "CO": "co",
    "SO2": "so2",
    "O3": "o3",
    "AQI": "aqi",
}

# Build a quick lookup: city name → (lat, lon)
CITY_COORDS = {city.name: (city.latitude, city.longitude) for city in INDIAN_CITIES}

# Batch size — insert this many rows at once
BATCH_SIZE = 5000


def load_historical_data():
    """
    Load cleaned CSV into the database in batches.
    """
    filepath = settings.PROCESSED_DATA_DIR / "city_hour_clean.csv"

    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        logger.error("Run historical_cleaner.py first!")
        return

    logger.info("=" * 50)
    logger.info("📥 Loading Historical Data into Database")
    logger.info("=" * 50)

    # Step 1: Make sure tables exist
    init_db()

    # Step 2: Read the cleaned CSV
    logger.info(f"Reading {filepath}...")
    df = pd.read_csv(filepath)
    logger.info(f"  Rows to load: {len(df)}")

    # Step 3: Rename columns to match database
    df = df.rename(columns=COLUMN_MAP)

    # Step 4: Convert datetime string to actual datetime objects
    df["measured_at"] = pd.to_datetime(df["measured_at"])

    # Step 5: Add latitude, longitude, source for each row
    df["source"] = "kaggle_historical"
    df["latitude"] = df["city"].map(lambda c: CITY_COORDS.get(c, (None, None))[0])
    df["longitude"] = df["city"].map(lambda c: CITY_COORDS.get(c, (None, None))[1])

    # Step 6: Insert in batches
    session = get_session()
    total_saved = 0
    total_skipped = 0

    try:
        for start in range(0, len(df), BATCH_SIZE):
            batch = df.iloc[start:start + BATCH_SIZE]
            records = []

            for _, row in batch.iterrows():
                # Skip cities we don't have coordinates for
                if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
                    total_skipped += 1
                    continue

                record = AirQualityReading(
                    city=row["city"],
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                    aqi=row["aqi"] if pd.notna(row["aqi"]) else None,
                    co=row["co"] if pd.notna(row["co"]) else None,
                    no=row["no"] if pd.notna(row["no"]) else None,
                    no2=row["no2"] if pd.notna(row["no2"]) else None,
                    o3=row["o3"] if pd.notna(row["o3"]) else None,
                    so2=row["so2"] if pd.notna(row["so2"]) else None,
                    pm2_5=row["pm2_5"] if pd.notna(row["pm2_5"]) else None,
                    pm10=row["pm10"] if pd.notna(row["pm10"]) else None,
                    nh3=row["nh3"] if pd.notna(row["nh3"]) else None,
                    measured_at=row["measured_at"],
                    source=row["source"],
                )
                records.append(record)

            session.bulk_save_objects(records)
            session.commit()
            total_saved += len(records)

            # Progress log every batch
            logger.info(f"  Progress: {total_saved}/{len(df)} rows saved...")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed at row {total_saved}: {e}")
    finally:
        session.close()

    logger.info("=" * 50)
    logger.info(f"✅ Done! Saved: {total_saved} | Skipped: {total_skipped}")
    logger.info("=" * 50)


# --- Run directly ---
if __name__ == "__main__":
    load_historical_data()
