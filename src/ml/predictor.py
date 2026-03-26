"""
PM2.5 Predictor
Loads the trained model and predicts PM2.5 from live or input data.

Usage:
    from src.ml.predictor import predict_pm25
    result = predict_pm25("Delhi", hour=8, month=1, no2=45.0, co=1.2, ...)
"""

import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime

from config import settings
from src.data.cities import INDIAN_CITIES
from src.utils.logger import logger


# City name → numeric code (must match training encoding)
CITY_CODES = {city.name: i for i, city in enumerate(
    sorted(INDIAN_CITIES, key=lambda c: c.name)
)}


def load_model(filename: str = "xgboost_pm25.joblib"):
    """Load the trained model from disk."""
    filepath = settings.MODELS_DIR / filename
    if not filepath.exists():
        logger.error(f"Model not found: {filepath}. Run train_model.py first!")
        return None
    model = joblib.load(filepath)
    logger.info(f"✅ Model loaded: {filepath}")
    return model


def predict_pm25(
    city: str,
    hour: int | None = None,
    month: int | None = None,
    day_of_week: int | None = None,
    no: float | None = None,
    no2: float | None = None,
    co: float | None = None,
    so2: float | None = None,
    o3: float | None = None,
    nh3: float | None = None,
    pm10: float | None = None,
) -> dict:
    """
    Predict PM2.5 for a city given current conditions.

    Args:
        city: City name (e.g., "Delhi")
        hour: Current hour (0-23). Auto-detected if None.
        month: Current month (1-12). Auto-detected if None.
        Other args: Current pollutant readings from live API.

    Returns:
        dict with predicted PM2.5 value and input details.
    """
    # Auto-detect time if not provided
    now = datetime.now()
    if hour is None:
        hour = now.hour
    if month is None:
        month = now.month
    if day_of_week is None:
        day_of_week = now.weekday()

    is_winter = 1 if month in [11, 12, 1, 2] else 0

    # Get city code
    city_code = CITY_CODES.get(city)
    if city_code is None:
        logger.warning(f"Unknown city: {city}. Using code 0.")
        city_code = 0

    # Build feature row (same order as training!)
    features = pd.DataFrame([{
        "city_code": city_code,
        "hour": hour,
        "month": month,
        "day_of_week": day_of_week,
        "is_winter": is_winter,
        "NO": no,
        "NO2": no2,
        "CO": co,
        "SO2": so2,
        "O3": o3,
        "NH3": nh3,
        "PM10": pm10,
    }])
    
    features = features.astype(float)

    # Load model and predict
    model = load_model()
    if model is None:
        return {"error": "Model not found"}

    predicted_pm25 = float(model.predict(features)[0])

    # Clamp to realistic range
    predicted_pm25 = max(0, min(predicted_pm25, 500))

    result = {
        "city": city,
        "predicted_pm25": round(predicted_pm25, 2),
        "hour": hour,
        "month": month,
        "is_winter": bool(is_winter),
    }

    logger.info(f"🔮 Prediction: {city} → PM2.5 = {predicted_pm25:.2f} μg/m³")
    return result


# --- Test directly ---
if __name__ == "__main__":
    # Test with some sample inputs
    print("Testing predictions:\n")

    # Test 1: Delhi in winter morning (should be HIGH)
    r1 = predict_pm25("Delhi", hour=8, month=1, no2=45, co=2.5, pm10=180)
    print(f"Delhi (Winter 8AM):  PM2.5 = {r1['predicted_pm25']} μg/m³")

    # Test 2: Chennai in summer afternoon (should be LOW)
    r2 = predict_pm25("Chennai", hour=14, month=7, no2=12, co=0.5, pm10=40)
    print(f"Chennai (Summer 2PM): PM2.5 = {r2['predicted_pm25']} μg/m³")

    # Test 3: Mumbai right now (auto-detect time)
    r3 = predict_pm25("Mumbai", no2=25, co=1.0)
    print(f"Mumbai (Now):        PM2.5 = {r3['predicted_pm25']} μg/m³")
