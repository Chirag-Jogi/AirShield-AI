"""
PM2.5 Predictor (Elite Optimized) 🔮🛡️
Loads the trained model once (Singleton) and predicts PM2.5 from input data.
"""

import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import settings
from src.data.cities import INDIAN_CITIES
from src.utils.logger import logger
from src.utils.time_utils import get_ist_now

# --- Global Singleton Model ---
_MODEL_CACHE = {}

# City name → numeric code (must match training encoding)
CITY_CODES = {city.name: i for i, city in enumerate(
    sorted(INDIAN_CITIES, key=lambda c: c.name)
)}

def get_model(filename: str = "xgboost_pm25.joblib"):
    """
    Singleton loader to prevent redundant disk I/O and log spam.
    Loads the model once and keeps it in memory.
    """
    if filename not in _MODEL_CACHE:
        filepath = settings.MODELS_DIR / filename
        if not filepath.exists():
            logger.error(f"Model not found: {filepath}. Prediction fallback active.")
            return None
        _MODEL_CACHE[filename] = joblib.load(filepath)
        logger.info(f"✅ Predictor Engine Cloud-Loaded: {filepath.name}")
    
    return _MODEL_CACHE[filename]

def predict_pm25(
    city: str,
    hour: int | None = None,
    month: int | None = None,
    day_of_week: int | None = None,
    # Pollutants
    no: float = 0.0,
    no2: float = 0.0,
    co: float = 0.0,
    so2: float = 0.0,
    o3: float = 0.0,
    nh3: float = 0.0,
    pm10: float = 0.0,
) -> dict:
    """
    Predict PM2.5 for a city given current conditions.
    Optimized for high-frequency forecast generation.
    """
    # 1. Auto-detect time context
    now = get_ist_now()
    h = hour if hour is not None else now.hour
    m = month if month is not None else now.month
    dow = day_of_week if day_of_week is not None else now.weekday()
    is_winter = 1 if m in [11, 12, 1, 2] else 0

    # 2. Map city to code
    city_code = CITY_CODES.get(city, 0)

    # 3. Load model (Singleton)
    model = get_model()
    if model is None:
        return {"city": city, "predicted_pm25": 0.0, "error": "Model missing"}

    # 4. Prepare Feature Matrix
    features = pd.DataFrame([{
        "city_code": float(city_code),
        "hour": float(h),
        "month": float(m),
        "day_of_week": float(dow),
        "is_winter": float(is_winter),
        "NO": float(no or 0),
        "NO2": float(no2 or 0),
        "CO": float(co or 0),
        "SO2": float(so2 or 0),
        "O3": float(o3 or 0),
        "NH3": float(nh3 or 0),
        "PM10": float(pm10 or 0),
    }])

    # 5. Predict
    try:
        raw_pred = float(model.predict(features)[0])
        clamped_pred = max(0.0, min(raw_pred, 550.0))
        return {
            "city": city,
            "predicted_pm25": round(clamped_pred, 2),
            "hour": h,
            "month": m,
            "is_winter": bool(is_winter)
        }
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return {"city": city, "predicted_pm25": 0.0, "error": str(e)}

if __name__ == "__main__":
    # Rapid-fire test to verify singleton behavior (log should only appear once)
    print("Testing Singleton Predictor...")
    for _ in range(5):
        predict_pm25("Delhi")
    print("Done. Check logs for redundant loads!")
