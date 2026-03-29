"""
Elite Data Engine Tests 🛡️🧪
Verifies the 'Fattest Dataset' consensus strategy and outlier detection.
"""

import pytest
from src.data.cleaner import clean_reading, resolve_consensus, clean_and_resolve

def test_clean_reading_normalization():
    """Verify OpenWeather 1-5 scale to EPA 0-500 conversion."""
    raw = {
        "city": "Delhi", "latitude": 28.6, "longitude": 77.2,
        "aqi": 3, "timestamp": "2024-01-01T12:00:00Z", "source": "openweathermap",
        "pm2_5": 25.0
    }
    cleaned = clean_reading(raw)
    assert cleaned["aqi"] == 125 # Midpoint for 'Moderate'
    assert cleaned["pm10"] is None # Auto-standardization
    assert "source" in cleaned

def test_outlier_clamping():
    """Verify that impossible AQI values are clamped."""
    raw = {
        "city": "Mumbai", "latitude": 19.0, "longitude": 72.8,
        "aqi": 999, "timestamp": "2024-01-01T12:00:00Z", "source": "aqicn"
    }
    cleaned = clean_reading(raw)
    assert cleaned["aqi"] == 500

def test_consensus_fattest_dataset():
    """Verify the 'Fattest Dataset' picker logic."""
    # Source A: Only PM2.5
    source_a = {
        "city": "Pune", "aqi": 100, "source": "source_a", "pm2_5": 10.0,
        "latitude": 18.5, "longitude": 73.8, "timestamp": "..."
    }
    # Source B: PM2.5, PM10, and NO2
    source_b = {
        "city": "Pune", "aqi": 110, "source": "source_b", "pm2_5": 12.0, "pm10": 20.0, "no2": 5.0,
        "latitude": 18.5, "longitude": 73.8, "timestamp": "..."
    }
    
    resolved = resolve_consensus([source_a, source_b])
    assert len(resolved) == 1
    assert resolved[0]["source"] == "source_b"
    assert resolved[0]["pm10"] == 20.0

def test_full_clean_and_resolve_flow():
    """End-to-end test of the data engine."""
    raw_data = [
        {"city": "Bangalore", "aqi": 2, "source": "openweathermap", "latitude": 12.9, "longitude": 77.5, "timestamp": "2024-01-01T12:00:00Z", "pm2_5": 15.0},
        {"city": "Bangalore", "aqi": 60, "source": "aqicn", "latitude": 12.9, "longitude": 77.5, "timestamp": "2024-01-01T12:00:00Z", "pm2_5": 16.0, "pm10": 30.0},
        {"city": "Kolkata", "aqi": 4, "source": "openweathermap", "latitude": 22.5, "longitude": 88.3, "timestamp": "2024-01-01T12:00:00Z", "pm2_5": 35.0}
    ]
    
    results = clean_and_resolve(raw_data)
    assert len(results) == 2
    # Bangalore should picked AQICN (more pollutants)
    bangalore = next(r for r in results if r["city"] == "Bangalore")
    assert bangalore["source"] == "aqicn"
    assert bangalore["aqi"] == 60
    # Kolkata should be cleaned normally
    kolkata = next(r for r in results if r["city"] == "Kolkata")
    assert kolkata["aqi"] == 175 # OW 4 -> 175
