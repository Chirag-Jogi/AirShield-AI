"""
Step 1: Migrate Historical SQLite Data to Supabase Cloud
"""
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from config import BASE_DIR

# 1. Load your Supabase URL from .env
load_dotenv()
cloud_url = os.getenv("DATABASE_URL")

# 2. Setup the two Database connections
local_db_path = BASE_DIR / "data" / "airshield.db"
local_engine = create_engine(f"sqlite:///{local_db_path}")

# Fix Supabase connection string format
if cloud_url.startswith("postgres://"):
    cloud_url = cloud_url.replace("postgres://", "postgresql://", 1)
cloud_engine = create_engine(cloud_url)

print("🚀 Starting Migration: Local SQLite -> Supabase Cloud")

# 3. Read the 313,000 rows from local SQLite
print("📖 Reading historical data from local database...")
df = pd.read_sql("SELECT * FROM air_quality_readings", con=local_engine)
print(f"✅ Found {len(df)} rows to migrate.")

# IMPORTANT FIX 1: Drop the 'id' column from SQLite
# This forces Supabase to generate fresh, clean IDs for the cloud!
if 'id' in df.columns:
    df = df.drop(columns=['id'])

# 4. Upload to Cloud in smaller chunks safely
print("☁️ Uploading to Supabase (this will take a few minutes)...")
df.to_sql(
    "air_quality_readings", 
    con=cloud_engine, 
    if_exists="append", # Add to the live data already there
    index=False,
    chunksize=1000, # IMPORTANT FIX 2: Lowered from 10,000 to 1,000 to fix Postgres limit
    method="multi"
)

print("🎉 Migration Complete! Your cloud database now has all historical data.")
