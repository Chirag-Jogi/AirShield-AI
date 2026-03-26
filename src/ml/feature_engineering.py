"""
Feature Engineering
Transforms raw cleaned data into ML-ready features.

This module is used by BOTH:
- Training pipeline (to prepare training data)
- Prediction pipeline (to prepare live data for prediction)

So we keep it separate — one place, used everywhere.
"""

import pandas as pd
from src.utils.logger import logger


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract time-based features from the datetime column.
    
    Why: ML models can't read "2020-01-15 08:00". But they CAN
    learn patterns from hour=8, month=1, day_of_week=2.
    
    These are the patterns we found in EDA:
    - Hour: pollution peaks at 7-9 AM and 9-11 PM
    - Month: winter (Nov-Feb) is worst
    - Day of week: weekday vs weekend might differ
    """
    # Make sure it's a datetime type
    df["measured_at"] = pd.to_datetime(df["measured_at"])


    df["hour"] = df["measured_at"].dt.hour           # 0-23
    df["month"] = df["measured_at"].dt.month          # 1-12
    df["day_of_week"] = df["measured_at"].dt.dayofweek  # 0=Monday, 6=Sunday
    df["is_winter"] = df["month"].isin([11, 12, 1, 2]).astype(int)  # 1=winter, 0=not

    logger.info("  Added time features: hour, month, day_of_week, is_winter")
    return df


def encode_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert city names to numbers.
    
    Why: ML models work with numbers, not text.
    "Delhi"=0, "Mumbai"=1, etc.
    
    We use pandas Categorical — it remembers the mapping
    so we can decode predictions back to city names later.
    """
    df["city_code"] = pd.Categorical(df["city"]).codes
    logger.info(f"  Encoded {df['city'].nunique()} cities to numeric codes")
    return df


def prepare_features(df: pd.DataFrame, target_col: str = "PM2.5") -> tuple:
    """
    Full feature preparation pipeline.
    
    Args:
        df: DataFrame with cleaned air quality data
        target_col: What we're trying to predict (default: PM2.5)
    
    Returns:
        X: Feature DataFrame (input to model)
        y: Target Series (what model predicts)
    """
    logger.info("🔧 Starting Feature Engineering...")

    # Step 1: Add time features
    df = add_time_features(df)

    # Step 2: Encode city names
    df = encode_city(df)

    # Step 3: Drop rows where target is missing
    before = len(df)
    df = df.dropna(subset=[target_col])
    dropped = before - len(df)
    if dropped > 0:
        logger.info(f"  Dropped {dropped} rows with missing {target_col}")

    # Step 4: Select features for the model
    feature_cols = [
        "city_code",    # which city
        "hour",         # time of day
        "month",        # month of year
        "day_of_week",  # weekday vs weekend
        "is_winter",    # winter flag
        "NO",           # pollutants that help predict PM2.5
        "NO2",
        "CO",
        "SO2",
        "O3",
        "NH3",
        "PM10",
    ]

    X = df[feature_cols]
    y = df[target_col]

    logger.info(f"  Features: {feature_cols}")
    logger.info(f"  Target: {target_col}")
    logger.info(f"  Final dataset: {len(X)} rows, {len(feature_cols)} features")
    logger.info("✅ Feature Engineering complete!")

    return X, y


# --- Test directly ---
if __name__ == "__main__":
    from config import settings

    # Load the cleaned CSV
    filepath = settings.PROCESSED_DATA_DIR / "city_hour_clean.csv"
    df = pd.read_csv(filepath)

    # Rename columns to match database format
    df = df.rename(columns={
        "City": "city",
        "Datetime": "measured_at",
        "PM2.5": "PM2.5",  # keep as-is for target
    })

    X, y = prepare_features(df)
    print(f"\nX shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"\nFirst 3 rows of X:\n{X.head(3)}")
    print(f"\nFirst 3 values of y:\n{y.head(3)}")
