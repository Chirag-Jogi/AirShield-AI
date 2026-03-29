"""
Elite Data Cleaner & Consensus Engine 🛡️🧬
Normalizes multi-source data and resolves discrepancies using the "Fattest Dataset" strategy.
Features: Outlier detection, AQI standardization, and multi-source consensus.
"""

from typing import List, Dict, Optional
from collections import defaultdict
from src.utils.logger import logger

# OpenWeatherMap uses European AQI (1-5)
# We convert to US EPA AQI (0-500) using midpoint mapping
# Midpoints derived from the 0-500 scale bands.
OPENWEATHER_TO_EPA = {
    1: 25,    # Good (0-50)
    2: 75,    # Fair (51-100)
    3: 125,   # Moderate (101-150)
    4: 175,   # Poor (151-200)
    5: 250,   # Very Poor (201-300)
}

# Thresholds for Outlier Detection
MAX_AQI_VALID = 500
POLLUTANT_LIST = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]

def clean_reading(data: dict) -> Optional[dict]:
    """
    Normalizes and validates a single air quality record.
    Filters out impossible values and standardized pollutant fields.
    """
    # 1. Mandatory Field Validation
    required_fields = ["city", "latitude", "longitude", "aqi", "timestamp"]
    if not all(data.get(field) is not None for field in required_fields):
        logger.warning(f"⚠️ Rejected incomplete record for {data.get('city', 'Unknown')}")
        return None

    # 2. Source-Specific AQI Normalization
    source = data.get("source", "unknown")
    if source == "openweathermap":
        raw_aqi = data["aqi"]
        data["aqi"] = OPENWEATHER_TO_EPA.get(raw_aqi, int(raw_aqi))
    
    # 3. Outlier and Bounds Guard (Elite Reliability)
    if not (0 <= data["aqi"] <= MAX_AQI_VALID):
        logger.warning(f"🚨 Outlier detected: AQI={data['aqi']} in {data['city']}. Clamping to 500.")
        data["aqi"] = min(MAX_AQI_VALID, max(0, data["aqi"]))

    # 4. Pollutant Sanitization
    for p in POLLUTANT_LIST:
        val = data.get(p)
        if val is not None and val < 0:
            logger.debug(f"Cleaning negative pollutant: {p}={val} in {data['city']}")
            data[p] = None
        # Ensure all pollutants exist in the dict for schema consistency
        if p not in data:
            data[p] = None

    return data

def resolve_consensus(readings: List[Dict]) -> List[Dict]:
    """
    Implements the 'Fattest Dataset' consensus strategy.
    Groups readings by city and picks the one with the most pollutant data points.
    """
    if not readings:
        return []

    # Grouping by city
    grouped = defaultdict(list)
    for r in readings:
        grouped[r['city']].append(r)

    resolved = []
    for city, city_readings in grouped.items():
        if len(city_readings) == 1:
            resolved.append(city_readings[0])
            continue
        
        # Consensus Logic: Pick the record with the most non-None pollutant values
        # This is the "Fattest Dataset" strategy.
        best_record = max(
            city_readings, 
            key=lambda r: sum(1 for p in POLLUTANT_LIST if r.get(p) is not None)
        )
        
        source_names = [r.get('source', 'unknown') for r in city_readings]
        logger.info(f"🧬 Consensus reached for {city}: Picked {best_record.get('source')} (Sources: {', '.join(source_names)})")
        resolved.append(best_record)

    return resolved

def clean_and_resolve(readings: List[Dict]) -> List[Dict]:
    """Entry point for the data cleaning and consensus pipeline."""
    # Step 1: Individual normalization
    cleaned = []
    for r in readings:
        result = clean_reading(r)
        if result:
            cleaned.append(result)
    
    # Step 2: Cross-source resolution
    resolved = resolve_consensus(cleaned)
    
    logger.info(f"✅ Data Engine: Processed {len(readings)} raw → {len(resolved)} elite artifacts.")
    return resolved