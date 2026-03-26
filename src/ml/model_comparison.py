"""
Model Comparison Script
Trains multiple regression models, compares them, and saves the best one.

Models compared:
1. Linear Regression (baseline)
2. Random Forest
3. XGBoost
4. LightGBM
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

from config import settings
from src.ml.feature_engineering import prepare_features
from src.utils.logger import logger


def load_data() -> pd.DataFrame:
    """Load cleaned CSV and rename columns."""
    filepath = settings.PROCESSED_DATA_DIR / "city_hour_clean.csv"
    logger.info(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    df = df.rename(columns={"City": "city", "Datetime": "measured_at"})
    return df


def evaluate(name: str, model, X_test, y_test) -> dict:
    """Evaluate a model and return metrics."""
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    logger.info(f"  {name:20s} → MAE={mae:.2f}  RMSE={rmse:.2f}  R²={r2:.4f}")
    return {"model_name": name, "mae": mae, "rmse": rmse, "r2": r2, "model": model}


def run_comparison():
    """Train all models, compare, and save the best one."""
    logger.info("=" * 60)
    logger.info("🏆 MODEL COMPARISON — Finding the best model")
    logger.info("=" * 60)

    # Step 1: Load and prepare data
    df = load_data()
    X, y = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"  Train: {len(X_train)} | Test: {len(X_test)}")
    logger.info("")

    # Step 2: Define all models to compare
    models = {
        "Linear Regression": LinearRegression(),

        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        ),

        "XGBoost": xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbosity=0,  # silent training
        ),

        "LightGBM": lgb.LGBMRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbosity=-1,  # silent training
        ),
    }

    # Step 3: Train and evaluate each model
    logger.info("📊 Results:")
    logger.info("-" * 60)
    results = []

    for name, model in models.items():
        logger.info(f"  Training {name}...")
        model.fit(X_train, y_train)
        result = evaluate(name, model, X_test, y_test)
        results.append(result)

    # Step 4: Find the winner (highest R²)
    logger.info("")
    logger.info("=" * 60)
    best = max(results, key=lambda x: x["r2"])
    logger.info(f"🏆 WINNER: {best['model_name']}")
    logger.info(f"   R² = {best['r2']:.4f} | MAE = {best['mae']:.2f} | RMSE = {best['rmse']:.2f}")
    logger.info("=" * 60)

    # Step 5: Save the best model
    filepath = settings.MODELS_DIR / "best_model.joblib"
    joblib.dump(best["model"], filepath)
    logger.info(f"💾 Best model saved: {filepath}")

    # Also save a summary
    summary = pd.DataFrame([
        {"Model": r["model_name"], "MAE": round(r["mae"], 2),
         "RMSE": round(r["rmse"], 2), "R²": round(r["r2"], 4)}
        for r in results
    ])
    summary = summary.sort_values("R²", ascending=False)
    summary_path = settings.MODELS_DIR / "comparison_results.csv"
    summary.to_csv(summary_path, index=False)
    logger.info(f"📋 Comparison saved: {summary_path}")

    print("\n" + summary.to_string(index=False))

    return best


# --- Run directly ---
if __name__ == "__main__":
    run_comparison()
