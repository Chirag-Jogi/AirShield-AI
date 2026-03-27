"""
Phase 6 MLOps: Continuous Training Pipeline with MLflow
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.xgboost
import joblib

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from config import settings
from src.ml.predictor import CITY_CODES

def train_and_track():
    print("🚀 Starting Continuous Training Pipeline...")
    
    # 1. Connect to our Cloud Database
    cloud_url = settings.DATABASE_URL
    if cloud_url.startswith("postgres://"):
        cloud_url = cloud_url.replace("postgres://", "postgresql://", 1)
    engine = create_engine(cloud_url)
    
    # 2. Download ALL data (Historical + Live newly scraped rows)
    # OPTIMIZATION: We use chunks so we don't crash your computer's RAM with 300,000+ rows!
    print("📡 Downloading latest data from Supabase in chunks...")
    chunks = pd.read_sql("SELECT * FROM air_quality_readings", con=engine, chunksize=50000)
    df = pd.concat(chunks, ignore_index=True)
    print(f"✅ Downloaded {len(df)} rows safely.")
    
    # 3. Data Cleaning & Feature Engineering
    print("🧹 Cleaning data and engineering features...")
    df = df.dropna(subset=['pm2_5', 'measured_at', 'city'])
    df['measured_at'] = pd.to_datetime(df['measured_at'])
    
    # Create Temporal Features
    df['hour'] = df['measured_at'].dt.hour
    df['month'] = df['measured_at'].dt.month
    df['day_of_week'] = df['measured_at'].dt.weekday
    df['is_winter'] = df['month'].isin([11, 12, 1, 2]).astype(int)
    
    # Create Spatial Feature (Match exact city mapping)
    df['city_code'] = df['city'].map(CITY_CODES).fillna(0).astype(int)
    
    # Map lowercase DB columns to the Uppercase names the model expects
    df = df.rename(columns={
        'no': 'NO', 'no2': 'NO2', 'co': 'CO', 
        'so2': 'SO2', 'o3': 'O3', 'nh3': 'NH3', 'pm10': 'PM10'
    })
    
    # Fill missing gases with medians
    gases = ['NO', 'NO2', 'CO', 'SO2', 'O3', 'NH3', 'PM10']
    for gas in gases:
        if gas in df.columns:
            df[gas] = df[gas].fillna(df[gas].median())
            
    # Define EXACT feature order matching the codebase
    features = ['city_code', 'hour', 'month', 'day_of_week', 'is_winter', 
                'NO', 'NO2', 'CO', 'SO2', 'O3', 'NH3', 'PM10']
    
    X = df[features]
    y = df['pm2_5']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Set up MLflow (Store logs locally so we can view them)
    print("📈 Connecting to MLflow Experiment Tracker...")
    mlflow.set_tracking_uri(f"sqlite:///{settings.DATA_DIR}/mlflow.db")
    mlflow.set_experiment("AirShield_PM25_Prediction")
    
    # 5. Train and Track
    with mlflow.start_run():
        print("🧠 Training XGBoost Model on new data...")
        params = {
            "n_estimators": 100,
            "max_depth": 7,
            "learning_rate": 0.05,
            "random_state": 42
        }
        
        mlflow.log_params(params)
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        r2 = r2_score(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        
        print(f"📊 New Model Metrics: R2 = {r2:.4f} | RMSE = {rmse:.4f}")
        mlflow.log_metric("R2_score", r2)
        mlflow.log_metric("RMSE", rmse)
        mlflow.xgboost.log_model(model, "xgboost-model")
        
        # 6. The Guardrail (Promote to production only if safe!)
        current_model_path = settings.MODELS_DIR / "xgboost_pm25.joblib"
        
        if r2 >= 0.70:
            print("🏆 Model passed accuracy threshold. Promoting to production!")
            joblib.dump(model, current_model_path)
        else:
            print("⚠️ Warning: Model rejected. Accuracy dropped below acceptable limits.")

if __name__ == "__main__":
    train_and_track()
