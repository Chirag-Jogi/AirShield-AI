"""
OpenWeatherMap Air Pollution Scraper
API Docs: https://openweathermap.org/api/air-pollution
Free tier: 60 calls/minute
"""

import requests
from datetime import datetime, timezone
from src.utils.logger import logger


# Major Indian cities with their coordinates (latitude, longitude)
INDIAN_CITIES = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Lucknow": (26.8467, 80.9462),
    "Jaipur": (26.9124, 75.7873),
}


def fetch_air_quality(api_key: str, lat: float, lon: float) -> dict | None:
    """
    Fetch current air quality data for given coordinates.
    
    Returns dict with pollutant data or None if API call fails.
    """
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises error if status != 200
        data = response.json()

        # Extract the pollution data from API response
        pollution = data["list"][0]
        components = pollution["components"]

        result = {
            "latitude": lat,
            "longitude": lon,
            "aqi": pollution["main"]["aqi"],  # 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
            "co": components.get("co"),        # Carbon Monoxide (μg/m³)
            "no": components.get("no"),        # Nitrogen Monoxide (μg/m³)
            "no2": components.get("no2"),      # Nitrogen Dioxide (μg/m³)
            "o3": components.get("o3"),        # Ozone (μg/m³)
            "so2": components.get("so2"),      # Sulphur Dioxide (μg/m³)
            "pm2_5": components.get("pm2_5"),  # Fine particles (μg/m³)
            "pm10": components.get("pm10"),    # Coarse particles (μg/m³)
            "nh3": components.get("nh3"),      # Ammonia (μg/m³)
            "timestamp": datetime.fromtimestamp(
                pollution["dt"], tz=timezone.utc
            ).isoformat(),
        }
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None


def fetch_all_cities(api_key: str) -> list[dict]:
    """Fetch air quality for all Indian cities."""
    results = []

    for city_name, (lat, lon) in INDIAN_CITIES.items():
        logger.info(f"Fetching data for {city_name}...")
        data = fetch_air_quality(api_key, lat, lon)

        if data:
            data["city"] = city_name
            results.append(data)
            logger.info(f"  ✅ {city_name}: AQI={data['aqi']}, PM2.5={data['pm2_5']}")
        else:
            logger.warning(f"  ❌ Failed to fetch {city_name}")

    logger.info(f"Fetched data for {len(results)}/{len(INDIAN_CITIES)} cities")
    return results


# --- Run this file directly to test ---
if __name__ == "__main__":
    from config import settings

    if not settings.OPENWEATHER_API_KEY:
        logger.error("No API key! Add OPENWEATHER_API_KEY to your .env file")
    else:
        logger.info("🚀 Testing OpenWeatherMap scraper...")
        data = fetch_all_cities(settings.OPENWEATHER_API_KEY)

        # Print a sample
        if data:
            sample = data[0]
            logger.info(f"Sample data: {sample}")