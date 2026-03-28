import os
from sqlalchemy import text
from src.database.connection import engine
from dotenv import load_dotenv

load_dotenv()

def patch():
    print("🏗️ Starting Database Migration...")
    query1 = text("ALTER TABLE users ADD COLUMN last_morning_at TIMESTAMP;")
    query2 = text("ALTER TABLE users ADD COLUMN last_alert_at TIMESTAMP;")
    
    with engine.connect() as conn:
        try:
            print("  -> Adding 'last_morning_at'...")
            conn.execute(query1)
            conn.commit()
        except Exception as e:
            print(f"  ⚠️ Could not add last_morning_at: {e}")

        try:
            print("  -> Adding 'last_alert_at'...")
            conn.execute(query2)
            conn.commit()
        except Exception as e:
            print(f"  ⚠️ Could not add last_alert_at: {e}")
            
    print("✅ Database Patch Complete!")

if __name__ == "__main__":
    patch()
