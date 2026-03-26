"""
Historical Data Cleaner
Cleans the Kaggle city_hour.csv dataset for ML training.

What it does:
1. Loads raw CSV from data/raw/
2. Drops columns our live APIs don't provide (Benzene, Toluene, Xylene)
3. Removes sensor error rows (impossible values like PM2.5=999)
4. Handles missing values (NaN)
5. Saves cleaned CSV to data/processed/
"""

import pandas as pd
from pathlib import Path
from config import settings
from src.utils.logger import logger


def load_raw_data() -> pd.DataFrame:
    """Load the raw city_hour.csv file."""
    filepath = settings.RAW_DATA_DIR / "city_hour.csv"

    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"Place city_hour.csv in {settings.RAW_DATA_DIR}")

    logger.info(f"Loading raw data from {filepath}...")
    df = pd.read_csv(filepath)
    logger.info(f"  Loaded: {len(df)} rows, {len(df.columns)} columns")
    return df


def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns that our live APIs don't provide.
    
    Why: Benzene, Toluene, Xylene are NOT available from 
    OpenWeatherMap or AQICN. If we train on them, our model
    will expect them during prediction — but we won't have them.
    Also AQI_Bucket is just a text label of AQI, redundant.
    """
    cols_to_drop = ["Benzene", "Toluene", "Xylene", "AQI_Bucket", "NOx"]
    existing = [c for c in cols_to_drop if c in df.columns]
    df = df.drop(columns=existing)
    logger.info(f"  Dropped columns: {existing}")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with impossible values (sensor errors).
    
    Why: During EDA we found PM2.5=999.99, AQI=3133.
    These are clearly sensor malfunctions — real PM2.5 rarely 
    exceeds 500 even in the worst pollution events.
    AQI by definition is 0-500 on the US EPA scale.
    """
    before = len(df)

    # AQI must be between 0 and 500
    df = df[(df["AQI"].isna()) | ((df["AQI"] >= 0) & (df["AQI"] <= 500))]

    # PM2.5 must be between 0 and 500 μg/m³
    df = df[(df["PM2.5"].isna()) | ((df["PM2.5"] >= 0) & (df["PM2.5"] <= 500))]

    # PM10 must be between 0 and 600 μg/m³
    df = df[(df["PM10"].isna()) | ((df["PM10"] >= 0) & (df["PM10"] <= 600))]

    after = len(df)
    removed = before - after
    logger.info(f"  Removed {removed} outlier rows ({removed/before*100:.2f}%)")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing (NaN) values.
    
    Strategy:
    - Rows where BOTH PM2.5 AND AQI are missing → drop them
      (these rows have almost no useful data)
    - Other NaN values → keep them as NaN for now
      (ML models like XGBoost can handle NaN natively)
    """
    before = len(df)

    # Drop rows where both PM2.5 and AQI are missing
    df = df.dropna(subset=["PM2.5", "AQI"], how="all")

    after = len(df)
    dropped = before - after
    logger.info(f"  Dropped {dropped} rows with both PM2.5 and AQI missing")

    # Log remaining NaN counts
    nan_counts = df.isna().sum()
    nan_cols = nan_counts[nan_counts > 0]
    if len(nan_cols) > 0:
        logger.info(f"  Remaining NaN counts:\n{nan_cols.to_string()}")

    return df


def clean_historical_data() -> pd.DataFrame:
    """
    Run the full cleaning pipeline.
    Returns the cleaned DataFrame.
    """
    logger.info("=" * 50)
    logger.info("🧹 Starting Historical Data Cleaning")
    logger.info("=" * 50)

    # Step 1: Load
    df = load_raw_data()

    # Step 1.5: Standardize city names
    df["City"] = df["City"].replace({"Bengaluru": "Bangalore"})
    logger.info("  Standardized city names (Bengaluru → Bangalore)")

    # Step 2: Drop unused columns
    df = drop_unused_columns(df)

    # Step 3: Remove outliers
    df = remove_outliers(df)

    # Step 4: Handle missing values
    df = handle_missing_values(df)

    # Step 5: Save to processed folder
    output_path = settings.PROCESSED_DATA_DIR / "city_hour_clean.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"✅ Saved cleaned data: {output_path}")
    logger.info(f"   Final: {len(df)} rows, {len(df.columns)} columns")
    logger.info("=" * 50)

    return df


# --- Run directly ---
if __name__ == "__main__":
    clean_historical_data()
