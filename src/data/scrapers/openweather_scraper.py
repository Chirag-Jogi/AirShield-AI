"""
OpenWeatherMap Air Pollution Scraper
API Docs: https://openweathermap.org/api/air-pollution
Free tier: 60 calls/minute
"""

import requests
from datetime import datetime, timezone

from src.data.cities import INDIAN_CITIES
from src.utils.logger import logger
from src.utils.retry import retry_on_failure


@retry_on_failure(exceptions=(requests.exceptions.RequestException,))
def fetch_air_quality(api_key: str, city_name: str, lat: float, lon: float) -> dict | None:
    """
    Fetch current air quality data for given coordinates.
    Decorated with retry — will attempt up to API_MAX_RETRIES times.
    Returns dict with pollutant data or None if all retries fail.
    """
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": api_key}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    pollution = data["list"][0]
    components = pollution["components"]

    return {
        "city": city_name,
        "latitude": lat,
        "longitude": lon,
        "aqi": pollution["main"]["aqi"],
        "co": components.get("co"),
        "no": components.get("no"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "so2": components.get("so2"),
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "nh3": components.get("nh3"),
        "timestamp": datetime.fromtimestamp(
            pollution["dt"], tz=timezone.utc
        ).isoformat(),
        "source": "openweathermap",
    }


def fetch_all_cities(api_key: str) -> list[dict]:
    """Fetch air quality for all configured cities."""
    results = []
    for city in INDIAN_CITIES:
        logger.info(f"[OpenWeather] Fetching {city.name}...")
        data = fetch_air_quality(api_key, city.name, city.latitude, city.longitude)
        if data:
            results.append(data)
            logger.info(f"  ✅ {city.name}: AQI={data['aqi']}, PM2.5={data['pm2_5']}")
        else:
            logger.warning(f"  ❌ Failed: {city.name} (all retries exhausted)")

    logger.info(f"[OpenWeather] Fetched {len(results)}/{len(INDIAN_CITIES)} cities")
    return results


if __name__ == "__main__":
    from config import settings
    if not settings.OPENWEATHER_API_KEY:
        logger.error("No API key! Add OPENWEATHER_API_KEY to your .env file")
    else:
        logger.info("🚀 Testing OpenWeatherMap scraper...")
        data = fetch_all_cities(settings.OPENWEATHER_API_KEY)
        if data:
            logger.info(f"Sample: {data[0]}")