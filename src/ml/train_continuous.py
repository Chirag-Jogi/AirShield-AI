"""
AirShield AI — Phase 6: Self-Evolution (Continuous Retraining) 🧬🛡️
Automatically pulls live data from Supabase, re-trains the XGBoost model, 
and promotes the 'Champion' model if accuracy thresholds are met.
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.xgboost
import joblib
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from config import settings
from src.ml.predictor import CITY_CODES
from src.utils.logger import logger

def get_db_engine():
    """Elite database engine creator with URL sanitization."""
    cloud_url = settings.DATABASE_URL
    if not cloud_url:
        raise ValueError("DATABASE_URL not set in .env")
    
    if cloud_url.startswith("postgres://"):
        cloud_url = cloud_url.replace("postgres://", "postgresql://", 1)
        
    return create_engine(cloud_url)

def check_data_readiness(min_required=50):
    """
    Checks if we have enough fresh data for a meaningful evolution.
    """
    engine = get_db_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM air_quality_readings"))
        count = result.scalar()
        
    logger.info(f"📊 Evolution Check: {count} total readings found in Supabase.")
    return count >= min_required, count

def train_and_track():
    """
    The core 'Self-Evolution' loop:
    Download -> Preprocess -> Train -> Evaluate -> Promote.
    """
    is_ready, count = check_data_readiness()
    if not is_ready:
        logger.warning(f"⚠️ Evolution Delayed: Need at least 50 readings (Have {count}). Keep the ETL running, buddy!")
        return False

    logger.info("🚀 Initiating Self-Evolution Pipeline...")
    
    try:
        # 1. Extraction
        engine = get_db_engine()
        logger.info("📡 Downloading latest data in high-performance chunks...")
        chunks = pd.read_sql("SELECT * FROM air_quality_readings", con=engine, chunksize=50000)
        df = pd.concat(chunks, ignore_index=True)
        
        # 2. Cleaning & Engineering
        logger.info("🧹 Preprocessing Elite Features...")
        df = df.dropna(subset=['pm2_5', 'measured_at', 'city'])
        df['measured_at'] = pd.to_datetime(df['measured_at'])
        
        df['hour'] = df['measured_at'].dt.hour
        df['month'] = df['measured_at'].dt.month
        df['day_of_week'] = df['measured_at'].dt.weekday
        df['is_winter'] = df['month'].isin([11, 12, 1, 2]).astype(int)
        df['city_code'] = df['city'].map(CITY_CODES).fillna(0).astype(int)
        
        # Mapping for model compatibility
        df = df.rename(columns={
            'no': 'NO', 'no2': 'NO2', 'co': 'CO', 
            'so2': 'SO2', 'o3': 'O3', 'nh3': 'NH3', 'pm10': 'PM10'
        })
        
        features = ['city_code', 'hour', 'month', 'day_of_week', 'is_winter', 
                    'NO', 'NO2', 'CO', 'SO2', 'O3', 'NH3', 'PM10']
        
        # Fill missing with median
        for f in features[5:]: # Only gas pollutants
            if f in df.columns:
                df[f] = df[f].fillna(df[f].median())
        
        X = df[features]
        y = df['pm2_5']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 3. Training & Tracking
        tracker_path = settings.DATA_DIR / "mlflow.db"
        mlflow.set_tracking_uri(f"sqlite:///{tracker_path}")
        mlflow.set_experiment("AirShield_Evolution")
        
        with mlflow.start_run():
            logger.info("🧠 Brain Training: Optimizing XGBoost for latest trends...")
            params = {
                "n_estimators": 150, # Boosted for evolution
                "max_depth": 7,
                "learning_rate": 0.05,
                "random_state": 42
            }
            mlflow.log_params(params)
            
            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train)
            
            # Eval
            preds = model.predict(X_test)
            r2 = r2_score(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            
            logger.info(f"📊 Challenger Model Stats: R2 = {r2:.4f} | RMSE = {rmse:.4f}")
            mlflow.log_metric("R2", r2)
            mlflow.log_metric("RMSE", rmse)
            
            # 4. Champion vs Challenger Guardrail
            current_model_path = settings.MODELS_DIR / "xgboost_pm25.joblib"
            
            # Elite Rule: Only promote if accuracy is decent (>0.70 R2)
            if r2 >= 0.70:
                logger.info("🏆 Model Evolved! Promoting the Challenger to Champion.")
                joblib.dump(model, current_model_path)
                mlflow.xgboost.log_model(model, "Champion-Model")
                return True
            else:
                logger.warning("⚠️ Evolution Rejected: Challenger accuracy didn't meet Elite standards.")
                return False

    except Exception as e:
        logger.error(f"❌ Evolution Crashed: {str(e)}")
        return False

if __name__ == "__main__":
    train_and_track()
