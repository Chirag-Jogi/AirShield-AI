"""
AQICN (World Air Quality Index) Scraper
API Docs: https://aqicn.org/json-api/doc/
Free tier: 1000 calls/minute
"""

import requests
from datetime import datetime, timezone

from src.data.cities import INDIAN_CITIES
from src.utils.logger import logger
from src.utils.retry import retry_on_failure


@retry_on_failure(exceptions=(requests.exceptions.RequestException,))
def fetch_air_quality(api_key: str, city_name: str, city_slug: str) -> dict | None:
    """
    Fetch current air quality for a city from AQICN.
    Decorated with retry — will attempt up to API_MAX_RETRIES times.
    Returns dict with pollutant data or None if all retries fail.
    """
    url = f"https://api.waqi.info/feed/{city_slug}/"
    params = {"token": api_key}

    response = requests.get(url, params=params, timeout=10)
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


def fetch_all_cities(api_key: str) -> list[dict]:
    """Fetch air quality for all configured cities."""
    results = []
    for city in INDIAN_CITIES:
        logger.info(f"[AQICN] Fetching {city.name}...")
        data = fetch_air_quality(api_key, city.name, city.aqicn_slug)
        if data:
            results.append(data)
            logger.info(f"  ✅ {city.name}: AQI={data['aqi']}, PM2.5={data['pm2_5']}")
        else:
            logger.warning(f"  ❌ Failed: {city.name} (all retries exhausted)")

    logger.info(f"[AQICN] Fetched {len(results)}/{len(INDIAN_CITIES)} cities")
    return results


if __name__ == "__main__":
    from config import settings
    if not settings.AQICN_API_KEY:
        logger.error("No AQICN key! Add AQICN_API_KEY to .env")
    else:
        logger.info("🚀 Testing AQICN scraper...")
        data = fetch_all_cities(settings.AQICN_API_KEY)
        if data:
            logger.info(f"Sample: {data[0]}")
