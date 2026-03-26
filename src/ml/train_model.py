"""
Model Training Script
Trains an XGBoost model to predict PM2.5 from air quality features.

What it does:
1. Loads cleaned data
2. Runs feature engineering
3. Splits into train/test sets (80/20)
4. Trains XGBoost model
5. Evaluates accuracy
6. Saves the trained model
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

from config import settings
from src.ml.feature_engineering import prepare_features
from src.utils.logger import logger


def load_data() -> pd.DataFrame:
    """Load cleaned CSV and prepare column names."""
    filepath = settings.PROCESSED_DATA_DIR / "city_hour_clean.csv"
    logger.info(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)

    # Rename to match our feature engineering expectations
    df = df.rename(columns={
        "City": "city",
        "Datetime": "measured_at",
    })
    return df


def train_xgboost(X_train, y_train, X_test, y_test):
    """
    Train an XGBoost regressor.
    
    Why these parameters:
    - n_estimators=200: number of trees (more = more accurate, but slower)
    - max_depth=6: how deep each tree goes (prevents overfitting)
    - learning_rate=0.1: how fast model learns (smaller = more careful)
    - early_stopping_rounds=20: stop if no improvement for 20 rounds
    """
    logger.info("🧠 Training XGBoost model...")

    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,  # use all CPU cores
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=50,  # print progress every 50 trees
    )

    return model


def evaluate_model(model, X_test, y_test):
    """
    Check how accurate the model is.
    
    Metrics explained:
    - MAE: Average error in μg/m³ (lower = better)
    - RMSE: Like MAE but penalizes big errors more (lower = better)
    - R²: How much of the pattern the model learned (1.0 = perfect)
    """
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5

    r2 = r2_score(y_test, predictions)

    logger.info("=" * 50)
    logger.info("📊 Model Evaluation Results:")
    logger.info(f"  MAE  = {mae:.2f} μg/m³  (average prediction error)")
    logger.info(f"  RMSE = {rmse:.2f} μg/m³  (penalized for big errors)")
    logger.info(f"  R²   = {r2:.4f}        (1.0 = perfect)")
    logger.info("=" * 50)

    return {"mae": mae, "rmse": rmse, "r2": r2}


def save_model(model, filename: str = "xgboost_pm25.joblib"):
    """Save trained model to disk."""
    filepath = settings.MODELS_DIR / filename
    joblib.dump(model, filepath)
    logger.info(f"💾 Model saved: {filepath}")
    return filepath


def run_training():
    """Full training pipeline."""
    logger.info("=" * 50)
    logger.info("🚀 Starting Model Training Pipeline")
    logger.info("=" * 50)

    # Step 1: Load data
    df = load_data()

    # Step 2: Feature engineering
    X, y = prepare_features(df)

    # Step 3: Split into train (80%) and test (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"  Train: {len(X_train)} rows | Test: {len(X_test)} rows")

    # Step 4: Train model
    model = train_xgboost(X_train, y_train, X_test, y_test)

    # Step 5: Evaluate
    metrics = evaluate_model(model, X_test, y_test)

    # Step 6: Save model
    save_model(model)

    return model, metrics


# --- Run directly ---
if __name__ == "__main__":
    run_training()
