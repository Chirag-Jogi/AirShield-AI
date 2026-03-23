"""
AQICN (World Air Quality Index) Scraper
API Docs: https://aqicn.org/json-api/doc/
Free tier: 1000 calls/minute
"""

import requests
from datetime import datetime, timezone
from src.utils.logger import logger


# Same cities, using AQICN station names
AQICN_CITIES = {
    "Delhi": "delhi",
    "Mumbai": "mumbai",
    "Bangalore": "bangalore",
    "Kolkata": "kolkata",
    "Chennai": "chennai",
    "Hyderabad": "hyderabad",
    "Pune": "pune",
    "Ahmedabad": "ahmedabad",
    "Lucknow": "lucknow",
    "Jaipur": "jaipur",
}


def fetch_air_quality(api_key: str, city_slug: str) -> dict | None:
    """
    Fetch current air quality for a city from AQICN.
    Returns dict with pollutant data or None if failed.
    """
    url = f"https://api.waqi.info/feed/{city_slug}/"
    params = {"token": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["status"] != "ok":
            logger.warning(f"AQICN returned status: {data['status']}")
            return None

        info = data["data"]
        iaqi = info.get("iaqi", {})  # Individual pollutant values

        result = {
            "aqi": info.get("aqi"),
            "pm2_5": iaqi.get("pm25", {}).get("v"),
            "pm10": iaqi.get("pm10", {}).get("v"),
            "co": iaqi.get("co", {}).get("v"),
            "no2": iaqi.get("no2", {}).get("v"),
            "o3": iaqi.get("o3", {}).get("v"),
            "so2": iaqi.get("so2", {}).get("v"),
            "no": None,   # AQICN doesn't provide NO
            "nh3": None,  # AQICN doesn't provide NH3
            "latitude": info.get("city", {}).get("geo", [None, None])[0],
            "longitude": info.get("city", {}).get("geo", [None, None])[1],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"AQICN API call failed: {e}")
        return None


def fetch_all_cities(api_key: str) -> list[dict]:
    """Fetch air quality for all cities from AQICN."""
    results = []

    for city_name, city_slug in AQICN_CITIES.items():
        logger.info(f"[AQICN] Fetching {city_name}...")
        data = fetch_air_quality(api_key, city_slug)

        if data:
            data["city"] = city_name
            data["source"] = "aqicn"
            results.append(data)
            logger.info(f"  ✅ {city_name}: AQI={data['aqi']}, PM2.5={data['pm2_5']}")
        else:
            logger.warning(f"  ❌ Failed: {city_name}")

    logger.info(f"[AQICN] Fetched {len(results)}/{len(AQICN_CITIES)} cities")
    return results


# --- Test directly ---
if __name__ == "__main__":
    from config import settings

    if not settings.AQICN_API_KEY:
        logger.error("No AQICN key! Add AQICN_API_KEY to .env")
    else:
        logger.info("🚀 Testing AQICN scraper...")
        data = fetch_all_cities(settings.AQICN_API_KEY)
        if data:
            logger.info(f"Sample: {data[0]}")
