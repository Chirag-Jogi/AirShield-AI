"""
Migration Patch v2 — Pure Perfection Upgrade
Adds the 'chat_history' column to the existing 'users' table in Supabase.
Run this ONCE to prepare your database for persistent memory.
"""

import os
from sqlalchemy import text
from src.database.connection import engine
from dotenv import load_dotenv

load_dotenv()

def migrate_v2():
    print("🏗️  Starting Database Migration: Pure Perfection Upgrade...")
    
    with engine.connect() as conn:
        print("🔍 Checking existing columns in 'users' table...")
        
        # Check if column exists (PostgreSQL syntax)
        check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='chat_history';")
        result = conn.execute(check_sql).fetchone()
        
        if result:
            print("✅ 'chat_history' column already exists. No action needed.")
        else:
            print("➕ Adding 'chat_history' column to 'users' table...")
            try:
                # Add column as TEXT with default empty JSON array
                add_sql = text("ALTER TABLE users ADD COLUMN chat_history TEXT DEFAULT '[]';")
                conn.execute(add_sql)
                conn.commit()
                print("🎉 SUCCESS: 'chat_history' column added permanently to Supabase!")
            except Exception as e:
                print(f"❌ Error adding column: {e}")
                print("💡 Hint: Ensure your DATABASE_URL is correct in .env")

if __name__ == "__main__":
    migrate_v2()
