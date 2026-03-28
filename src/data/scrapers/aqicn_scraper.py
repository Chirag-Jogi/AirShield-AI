"""
AQICN (World Air Quality Index) Scraper (Async) — High-Resilience implementation.
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
async def fetch_air_quality(api_key: str, city_name: str, city_slug: str) -> dict | None:
    """
    Fetch current air quality for a city from AQICN using global async client.
    Decorated with sentinel_retry for professional-grade backoff.
    """
    url = f"https://api.waqi.info/feed/{city_slug}/"
    params = {"token": api_key}
    
    client = await get_http_client()
    
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "ok":
            logger.warning(f"AQICN returned status: {data['status']} for {city_name}")
            return None

        info = data["data"]
        iaqi = info.get("iaqi", {})

        return {
            "city": city_name,
            "aqi": info.get("aqi"),
            "pm2_5": iaqi.get("pm25", {}).get("v"),
            "pm10": iaqi.get("pm10", {}).get("v"),
            "co": iaqi.get("co", {}).get("v"),
            "no2": iaqi.get("no2", {}).get("v"),
            "o3": iaqi.get("o3", {}).get("v"),
            "so2": iaqi.get("so2", {}).get("v"),
            "no": None,
            "nh3": None,
            "latitude": info.get("city", {}).get("geo", [None, None])[0],
            "longitude": info.get("city", {}).get("geo", [None, None])[1],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "aqicn",
        }
    except Exception as e:
        logger.warning(f"[AQICN] Failed to fetch {city_name}: {str(e)}")
        raise

async def fetch_all_cities_async(api_key: str) -> list[dict]:
    """Fetch air quality for all configured cities concurrently."""
    semaphore = asyncio.Semaphore(10) # Limit concurrency
    
    async def sem_fetch(city):
        async with semaphore:
            logger.info(f"[AQICN] Fetching {city.name}...")
            try:
                data = await fetch_air_quality(api_key, city.name, city.aqicn_slug)
                if data:
                    logger.info(f"  ✅ {city.name}: AQI={data['aqi']}")
                return data
            except:
                return None

    tasks = [sem_fetch(city) for city in INDIAN_CITIES]
    results = await asyncio.gather(*tasks)
    
    valid_results = [r for r in results if r is not None]
    logger.info(f"[AQICN] Concurrently fetched {len(valid_results)}/{len(INDIAN_CITIES)} cities")
    return valid_results

# Backward compatibility
def fetch_all_cities(api_key: str) -> list[dict]:
    return asyncio.run(fetch_all_cities_async(api_key))

if __name__ == "__main__":
    from config import settings
    if not settings.AQICN_API_KEY:
        logger.error("No AQICN key!")
    else:
        logger.info("🚀 Testing Async AQICN scraper...")
        results = asyncio.run(fetch_all_cities_async(settings.AQICN_API_KEY))
        if results:
            logger.info(f"Sample: {results[0]}")
