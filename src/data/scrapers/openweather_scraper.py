"""
OpenWeatherMap Air Pollution Scraper (Async) — High-Resilience implementation.
Follows the "AirShield Upgrade Prompt" standards: Async-first and Concurrent.
"""

import httpx
import asyncio
from datetime import datetime, timezone
from src.data.cities import INDIAN_CITIES
from src.utils.logger import logger
from src.utils.retry import sentinel_retry
from src.utils.http_client import get_http_client

@sentinel_retry(exceptions=(httpx.HTTPError, asyncio.TimeoutError))
async def fetch_air_quality(api_key: str, city_name: str, lat: float, lon: float) -> dict | None:
    """
    Fetch current air quality data for given coordinates using the global async client.
    Decorated with sentinel_retry for professional-grade backoff.
    """
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": api_key}
    
    client = await get_http_client()
    
    try:
        response = await client.get(url, params=params)
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
    except Exception as e:
        logger.warning(f"[OpenWeather] Failed to fetch {city_name}: {str(e)}")
        raise # Reraise for the retry decorator

async def fetch_all_cities_async(api_key: str) -> list[dict]:
    """
    Fetch air quality for all configured cities concurrently.
    This is the core "Elite" speed upgrade.
    """
    semaphore = asyncio.Semaphore(10) # Limit concurrency to avoid rate limits
    
    async def sem_fetch(city):
        async with semaphore:
            logger.info(f"[OpenWeather] Fetching {city.name}...")
            try:
                data = await fetch_air_quality(api_key, city.name, city.latitude, city.longitude)
                if data:
                    logger.info(f"  ✅ {city.name}: AQI={data['aqi']}")
                return data
            except:
                return None

    tasks = [sem_fetch(city) for city in INDIAN_CITIES]
    results = await asyncio.gather(*tasks)
    
    # Filter out None values
    valid_results = [r for r in results if r is not None]
    logger.info(f"[OpenWeather] Concurrently fetched {len(valid_results)}/{len(INDIAN_CITIES)} cities")
    return valid_results

# Backward compatibility for sync-based entry points (if any remain)
def fetch_all_cities(api_key: str) -> list[dict]:
    """Sync wrapper for the async fetch."""
    return asyncio.run(fetch_all_cities_async(api_key))

if __name__ == "__main__":
    from config import settings
    if not settings.OPENWEATHER_API_KEY:
        logger.error("No API key!")
    else:
        logger.info("🚀 Testing Async OpenWeatherMap scraper...")
        results = asyncio.run(fetch_all_cities_async(settings.OPENWEATHER_API_KEY))
        if results:
            logger.info(f"Sample: {results[0]}")