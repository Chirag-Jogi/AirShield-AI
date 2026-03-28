"""
ETL Pipeline (Async) — Extract, Transform, Load
High-Performance orchestrator with concurrent extraction and fault isolation.
Follows the "AirShield Upgrade Prompt" standards: Concurrent and Resilient.
"""

import time
import asyncio
from dataclasses import dataclass, field
from config import settings
from src.data.scrapers import openweather_scraper, aqicn_scraper
from src.data.cleaner import clean_all_readings
from src.database.queries import save_readings
from src.utils.logger import logger
from src.utils.http_client import SentinelClient

@dataclass
class PipelineResult:
    """Structured result of a pipeline run for observability."""
    sources_attempted: int = 0
    sources_succeeded: int = 0
    raw_readings: int = 0
    cleaned_readings: int = 0
    saved_readings: int = 0
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0

    @property
    def success(self) -> bool:
        return self.saved_readings > 0 and self.sources_succeeded > 0

async def _extract_source_async(name: str, fetch_fn, api_key: str) -> list[dict]:
    """
    Extract data from a single source asynchronously with fault isolation.
    """
    try:
        logger.info(f"📡 Extracting from {name}...")
        data = await fetch_fn(api_key)
        logger.info(f"  → {name}: {len(data)} readings extracted")
        return data
    except Exception as e:
        logger.error(f"  ❌ {name} extraction failed completely: {e}")
        return []

async def run_pipeline_async() -> PipelineResult:
    """
    Run the full ETL pipeline asynchronously:
    1. EXTRACT — Scrape data from all APIs concurrently.
    2. TRANSFORM — Clean and normalize.
    3. LOAD — Save to database.
    """
    result = PipelineResult()
    start_time = time.time()

    logger.info("=" * 50)
    logger.info("🚀 Starting AirShield AI Data Pipeline (Async)")
    logger.info("=" * 50)

    # Prepare extraction tasks
    extraction_tasks = []
    if settings.OPENWEATHER_API_KEY:
        extraction_tasks.append(_extract_source_async(
            "OpenWeatherMap", openweather_scraper.fetch_all_cities_async, settings.OPENWEATHER_API_KEY
        ))
    if settings.AQICN_API_KEY:
        extraction_tasks.append(_extract_source_async(
            "AQICN", aqicn_scraper.fetch_all_cities_async, settings.AQICN_API_KEY
        ))

    result.sources_attempted = len(extraction_tasks)

    # 1. EXTRACT (Concurrent)
    if not extraction_tasks:
        logger.warning("⚠️ No extraction sources configured!")
        return result

    raw_results = await asyncio.gather(*extraction_tasks)
    
    all_readings = []
    for data in raw_results:
        if data:
            result.sources_succeeded += 1
            all_readings.extend(data)
    
    result.raw_readings = len(all_readings)

    if not all_readings:
        logger.error("❌ No data collected from any source!")
        await SentinelClient.close_client()
        return result

    # 2. TRANSFORM
    cleaned = clean_all_readings(all_readings)
    result.cleaned_readings = len(cleaned)

    # 3. LOAD
    result.saved_readings = save_readings(cleaned)

    # Clean up HTTP connections
    await SentinelClient.close_client()

    result.duration_seconds = time.time() - start_time
    logger.info("=" * 50)
    logger.info(
        f"✅ Pipeline complete | "
        f"Sources: {result.sources_succeeded}/{result.sources_attempted} | "
        f"Raw: {result.raw_readings} → Saved: {result.saved_readings} | "
        f"Duration: {result.duration_seconds:.1f}s"
    )
    logger.info("=" * 50)

    return result

def run_pipeline() -> PipelineResult:
    """Sync entry point for the pipeline."""
    return asyncio.run(run_pipeline_async())

if __name__ == "__main__":
    from src.database.connection import init_db
    init_db()
    run_pipeline()