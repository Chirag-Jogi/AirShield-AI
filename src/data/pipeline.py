"""
Elite ETL Pipeline — Resilient Data Harvesting 📡🚀
Features: Concurrent multi-source extraction, Consensus-based cleaning, and Async Loading.
Follows the "AirShield Upgrade Prompt" standards for production-grade resilience.
"""

import time
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass, field

from config import settings
from src.data.scrapers import openweather_scraper, aqicn_scraper
from src.data.cleaner import clean_and_resolve
from src.database import queries
from src.database.connection import AsyncSessionLocal
from src.utils.logger import logger
from src.utils.http_client import SentinelClient

@dataclass
class PipelineResult:
    """Structured result of a pipeline run for observability."""
    sources_attempted: int = 0
    sources_succeeded: int = 0
    raw_readings: int = 0
    resolved_readings: int = 0
    saved_readings: int = 0
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0

    @property
    def success(self) -> bool:
        return self.saved_readings > 0 and self.sources_succeeded > 0

async def _extract_async(name: str, fetch_fn, api_key: str) -> list[dict]:
    """Extract data from a single source asynchronously with fault isolation."""
    try:
        logger.info(f"📡 Extracting from {name}...")
        data = await fetch_fn(api_key)
        logger.info(f"  → {name}: {len(data)} readings extracted")
        return data
    except Exception as e:
        logger.error(f"  ❌ {name} extraction failed: {str(e)}")
        return []

async def run_pipeline_async() -> PipelineResult:
    """
    Elite ETL Flow: 
    1. EXTRACT (Concurrently from OpenWeather and AQICN)
    2. RESOLVE (Consensus-based cleaning)
    3. LOAD (Async commit to Supabase/SQLite)
    """
    result = PipelineResult()
    start_time = time.time()

    logger.info("=" * 50)
    logger.info(f"🚀 Starting ELITE Data Pipeline (Freq: 15-Min Bursts)")
    logger.info("=" * 50)

    # 1. EXTRACT (Execution of multiple concurrent sources)
    extraction_tasks = []
    if settings.OPENWEATHER_API_KEY:
        extraction_tasks.append(_extract_async(
            "OpenWeatherMap", openweather_scraper.fetch_all_cities_async, settings.OPENWEATHER_API_KEY
        ))
    if settings.AQICN_API_KEY:
        extraction_tasks.append(_extract_async(
            "AQICN", aqicn_scraper.fetch_all_cities_async, settings.AQICN_API_KEY
        ))

    result.sources_attempted = len(extraction_tasks)
    if not extraction_tasks:
        logger.warning("⚠️ No extraction sources configured! Check your .env file.")
        return result

    raw_results = await asyncio.gather(*extraction_tasks)
    
    all_raw_readings = []
    for data in raw_results:
        if data:
            result.sources_succeeded += 1
            all_raw_readings.extend(data)
    
    result.raw_readings = len(all_raw_readings)
    if not all_raw_readings:
        logger.error("❌ All sources failed. System blind. 🚨")
        return result

    # 2. TRANSFORM & RESOLVE (Consensus Engine)
    resolved_readings = clean_and_resolve(all_raw_readings)
    result.resolved_readings = len(resolved_readings)

    # 3. LOAD (High-Performance Async Commits)
    async with AsyncSessionLocal() as session:
        result.saved_readings = await queries.save_readings(session, resolved_readings)

    result.duration_seconds = time.time() - start_time
    logger.info("=" * 50)
    logger.info(
        f"✅ Pipeline complete | Sources: {result.sources_succeeded}/{result.sources_attempted} | "
        f"Resolved: {result.resolved_readings} → Saved: {result.saved_readings} | "
        f"Duration: {result.duration_seconds:.1f}s"
    )
    logger.info("=" * 50)

    return result

def run_pipeline():
    """Sync entry point for scheduler jobs."""
    return asyncio.run(run_pipeline_async())

if __name__ == "__main__":
    from src.database.connection import init_db
    # Manual trigger for testing
    async def manual_run():
        await init_db()
        await run_pipeline_async()
    
    asyncio.run(manual_run())