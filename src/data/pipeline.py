"""
ETL Pipeline — Extract, Transform, Load
The main pipeline that runs the full data collection flow.
"""

from config import settings
from src.data.scrapers import openweather_scraper, aqicn_scraper
from src.data.cleaner import clean_all_readings
from src.database.connection import init_db
from src.database.queries import save_readings
from src.utils.logger import logger


def run_pipeline():
    """
    Run the full ETL pipeline:
    1. EXTRACT — Scrape data from all APIs
    2. TRANSFORM — Clean and normalize the data
    3. LOAD — Save to database
    """
    logger.info("=" * 50)
    logger.info("🚀 Starting AirShield AI Data Pipeline")
    logger.info("=" * 50)

    # Make sure database tables exist
    init_db()

    all_readings = []

    # --- EXTRACT: Pull from OpenWeatherMap ---
    if settings.OPENWEATHER_API_KEY:
        logger.info("📡 Source 1: OpenWeatherMap")
        ow_data = openweather_scraper.fetch_all_cities(settings.OPENWEATHER_API_KEY)
        all_readings.extend(ow_data)
    else:
        logger.warning("⚠️ Skipping OpenWeatherMap (no API key)")

    # --- EXTRACT: Pull from AQICN ---
    if settings.AQICN_API_KEY:
        logger.info("📡 Source 2: AQICN")
        aqicn_data = aqicn_scraper.fetch_all_cities(settings.AQICN_API_KEY)
        all_readings.extend(aqicn_data)
    else:
        logger.warning("⚠️ Skipping AQICN (no API key)")

    if not all_readings:
        logger.error("❌ No data collected from any source!")
        return

    logger.info(f"📊 Total raw readings: {len(all_readings)}")

    # --- TRANSFORM: Clean and normalize ---
    cleaned = clean_all_readings(all_readings)

    # --- LOAD: Save to database ---
    saved = save_readings(cleaned)

    logger.info("=" * 50)
    logger.info(f"✅ Pipeline complete! Saved {saved} readings to database")
    logger.info("=" * 50)

    return saved


# --- Run directly ---
if __name__ == "__main__":
    run_pipeline()