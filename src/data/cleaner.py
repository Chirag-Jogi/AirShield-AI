"""
Data Cleaner & Normalizer
Cleans raw API data before saving to database.
Converts different AQI scales to US EPA standard (0-500).
"""

from src.utils.logger import logger


# OpenWeatherMap uses European AQI (1-5)
# We convert to US EPA AQI (0-500) using midpoint mapping
OPENWEATHER_TO_EPA = {
    1: 25,    # Good → 0-50, midpoint 25
    2: 75,    # Fair → 51-100, midpoint 75
    3: 125,   # Moderate → 101-150, midpoint 125
    4: 175,   # Poor → 151-200, midpoint 175
    5: 250,   # Very Poor → 201-300, midpoint 250
}


def clean_reading(data: dict) -> dict | None:
    """
    Clean and validate a single air quality reading.
    Returns cleaned data or None if data is too bad to use.
    """
    # Step 1: Check required fields exist
    required = ["city", "latitude", "longitude", "aqi", "timestamp"]
    for field in required:
        if data.get(field) is None:
            logger.warning(f"Missing required field '{field}' for {data.get('city', 'unknown')}")
            return None

    # Step 2: Normalize AQI to US EPA scale (0-500)
    source = data.get("source", "openweathermap")
    if source == "openweathermap":
        raw_aqi = data["aqi"]
        data["aqi"] = OPENWEATHER_TO_EPA.get(raw_aqi, raw_aqi)

    # Step 3: Validate pollutant ranges (can't be negative)
    pollutants = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]
    for p in pollutants:
        value = data.get(p)
        if value is not None and value < 0:
            logger.warning(f"Negative {p}={value} for {data['city']}, setting to None")
            data[p] = None

    # Step 4: Set source if missing
    if "source" not in data:
        data["source"] = "openweathermap"

    return data


def clean_all_readings(readings: list[dict]) -> list[dict]:
    """Clean a list of readings. Removes invalid ones."""
    cleaned = []
    for data in readings:
        result = clean_reading(data)
        if result:
            cleaned.append(result)

    rejected = len(readings) - len(cleaned)
    if rejected > 0:
        logger.warning(f"Rejected {rejected}/{len(readings)} invalid readings")

    logger.info(f"✅ Cleaned {len(cleaned)} readings (AQI normalized to US EPA scale)")
    return cleaned