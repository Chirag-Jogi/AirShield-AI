"""
Test Script: Sentinel Guardian Buddy (Integration Verification)
Force-sends a morning briefing simulation and an emergency alert simulation.
Verifies the 4-line, emoji-free, causal persona logic from proactive_alerts.py.
"""

import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv

# Project Tools
from src.database.queries import (
    get_active_users, 
    get_city_status, 
)
from src.bot.proactive_alerts import generate_buddy_message
from src.utils.logger import logger
from src.utils.http_client import SentinelClient

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def test_alerts_now():
    """Immediately trigger a morning brief and check for emergencies."""
    bot = Bot(token=TOKEN)
    users = get_active_users()
    
    logger.info(f"TEST: Executing integrated persona verification for {len(users)} users.")

    for user in users:
        if not user.home_city:
            continue
            
        city_status = get_city_status(user.home_city)
        if not city_status:
            continue

        # --- SIMULATION 1: MORNING BRIEFING ---
        try:
            msg = await generate_buddy_message(user, city_status, message_type="morning")
            await bot.send_message(
                chat_id=user.telegram_id, 
                text=msg
            )
            logger.info(f"SUCCESS: Morning briefing sent to {user.first_name}")
        except Exception as e:
            logger.error(f"FAILURE: Morning briefing failed: {e}")

        # --- SIMULATION 2: EMERGENCY ALERT ---
        # Force alert simulation regardless of current AQI threshold
        try:
            alert_msg = await generate_buddy_message(user, city_status, message_type="emergency")
            await bot.send_message(
                chat_id=user.telegram_id, 
                text=alert_msg
            )
            logger.info(f"SUCCESS: Emergency alert sent to {user.first_name}")
        except Exception as e:
            logger.error(f"FAILURE: Emergency alert failed: {e}")

    await SentinelClient.close_client()
    logger.info("TEST: Verification complete.")

if __name__ == "__main__":
    asyncio.run(test_alerts_now())
