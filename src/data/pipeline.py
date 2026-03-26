"""
ETL Pipeline — Extract, Transform, Load
Production-grade orchestrator with fault isolation and metrics.
"""

import time
from dataclasses import dataclass, field

from config import settings
from src.data.scrapers import openweather_scraper, aqicn_scraper
from src.data.cleaner import clean_all_readings
from src.database.queries import save_readings
from src.utils.logger import logger


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


def _extract_source(name: str, fetch_fn, api_key: str) -> list[dict]:
    """
    Extract data from a single source with fault isolation.
    If one source fails, the other still runs.
    """
    try:
        logger.info(f"📡 Extracting from {name}...")
        data = fetch_fn(api_key)
        logger.info(f"  → {name}: {len(data)} readings extracted")
        return data
    except Exception as e:
        logger.error(f"  ❌ {name} extraction failed completely: {e}")
        return []


def run_pipeline() -> PipelineResult:
    """
    Run the full ETL pipeline:
    1. EXTRACT — Scrape data from all APIs (fault-isolated per source)
    2. TRANSFORM — Clean and normalize
    3. LOAD — Save to database (per-record fault tolerance)

    Returns PipelineResult with full metrics.
    """
    result = PipelineResult()
    start_time = time.time()

    logger.info("=" * 50)
    logger.info("🚀 Starting AirShield AI Data Pipeline")
    logger.info("=" * 50)

    all_readings: list[dict] = []

    # --- EXTRACT (each source isolated) ---
    sources = []
    if settings.OPENWEATHER_API_KEY:
        sources.append(("OpenWeatherMap", openweather_scraper.fetch_all_cities, settings.OPENWEATHER_API_KEY))
    else:
        logger.warning("⚠️ Skipping OpenWeatherMap (no API key)")

    if settings.AQICN_API_KEY:
        sources.append(("AQICN", aqicn_scraper.fetch_all_cities, settings.AQICN_API_KEY))
    else:
        logger.warning("⚠️ Skipping AQICN (no API key)")

    result.sources_attempted = len(sources)

    for name, fetch_fn, api_key in sources:
        data = _extract_source(name, fetch_fn, api_key)
        if data:
            result.sources_succeeded += 1
            all_readings.extend(data)
        else:
            result.errors.append(f"{name}: zero readings extracted")

    result.raw_readings = len(all_readings)

    if not all_readings:
        logger.error("❌ No data collected from any source!")
        result.duration_seconds = time.time() - start_time
        return result

    # --- TRANSFORM ---
    cleaned = clean_all_readings(all_readings)
    result.cleaned_readings = len(cleaned)

    # --- LOAD ---
    result.saved_readings = save_readings(cleaned)

    result.duration_seconds = time.time() - start_time

    logger.info("=" * 50)
    logger.info(
        f"✅ Pipeline complete | "
        f"Sources: {result.sources_succeeded}/{result.sources_attempted} | "
        f"Raw: {result.raw_readings} → Cleaned: {result.cleaned_readings} → Saved: {result.saved_readings} | "
        f"Duration: {result.duration_seconds:.1f}s"
    )
    if result.errors:
        logger.warning(f"⚠️ Errors: {result.errors}")
    logger.info("=" * 50)

    return result


if __name__ == "__main__":
    from src.database.connection import init_db
    init_db()
    run_pipeline()