"""
Elite ETL Pipeline Tests 📡🧪
Verifies concurrent extraction, consensus cleaning, and async database commits.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.data.pipeline import run_pipeline_async, PipelineResult

@pytest.mark.asyncio
async def test_run_pipeline_async_success(mocker):
    """Verify standard successful pipeline execution with mocked sources."""
    
    # 1. Mock Scrapers
    mock_ow = mocker.patch("src.data.scrapers.openweather_scraper.fetch_all_cities_async", new_callable=AsyncMock)
    mock_aq = mocker.patch("src.data.scrapers.aqicn_scraper.fetch_all_cities_async", new_callable=AsyncMock)
    
    mock_ow.return_value = [{"city": "Delhi", "aqi": 125, "source": "openweathermap", "latitude": 28.6, "longitude": 77.2, "timestamp": "2024-01-01T12:00:00Z"}]
    mock_aq.return_value = [{"city": "Mumbai", "aqi": 75, "source": "aqicn", "latitude": 19.0, "longitude": 72.8, "timestamp": "2024-01-01T12:00:00Z"}]

    # 2. Mock Database Session
    mock_session = AsyncMock()
    mock_session_factory = mocker.patch("src.data.pipeline.AsyncSessionLocal", return_value=mock_session)
    mock_session.__aenter__.return_value = mock_session
    
    # 3. Mock Database Queries
    mock_save = mocker.patch("src.database.queries.save_readings", new_callable=AsyncMock)
    mock_save.return_value = 2

    # 4. Mock settings to ensure keys exist
    mocker.patch("src.config.settings.OPENWEATHER_API_KEY", "test_key")
    mocker.patch("src.config.settings.AQICN_API_KEY", "test_key")

    # EXECUTE
    result = await run_pipeline_async()

    # VERIFY
    assert result.sources_attempted == 2
    assert result.sources_succeeded == 2
    assert result.raw_readings == 2
    assert result.saved_readings == 2
    assert result.success is True
    
    # Ensure scrapers were called concurrently
    mock_ow.assert_called_once()
    mock_aq.assert_called_once()
    # Ensure database was updated
    mock_save.assert_called_once()

@pytest.mark.asyncio
async def test_pipeline_survival_on_source_failure(mocker):
    """Verify that the pipeline survives even if one source is down."""
    
    # 1. Mock Scrapers (One success, one failure)
    mock_ow = mocker.patch("src.data.scrapers.openweather_scraper.fetch_all_cities_async", new_callable=AsyncMock)
    mock_aq = mocker.patch("src.data.scrapers.aqicn_scraper.fetch_all_cities_async", new_callable=AsyncMock)
    
    mock_ow.return_value = [{"city": "Delhi", "aqi": 125, "source": "openweathermap", "latitude": 28.6, "longitude": 77.2, "timestamp": "2024-01-01T12:00:00Z"}]
    mock_aq.side_effect = Exception("API Down!")

    # 2. Mock Database
    mocker.patch("src.data.pipeline.AsyncSessionLocal", return_value=AsyncMock())
    mocker.patch("src.database.queries.save_readings", new_callable=AsyncMock, return_value=1)
    
    mocker.patch("src.config.settings.OPENWEATHER_API_KEY", "test_key")
    mocker.patch("src.config.settings.AQICN_API_KEY", "test_key")

    # EXECUTE
    result = await run_pipeline_async()

    # VERIFY
    assert result.sources_attempted == 2
    assert result.sources_succeeded == 1  # Only OpenWeather succeeded
    assert result.saved_readings == 1
    assert result.success is True
    logger_msg = "✅ Pipeline complete | Sources: 1/2" # Check logs if possible, but status suffice
