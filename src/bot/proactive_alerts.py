"""
Elite Sentinel Proactive Alerts — The "Steel Memory" Guardian 🛡️🕒
An automated system that pushes morning briefings and real-time hazardous alerts.
Fully Async, SQLAlchemy 2.0 compliant, and powered by the Swiggy-style AI Persona.
"""

import asyncio
from datetime import datetime, timezone
import pytz
from telegram import Bot
from telegram.constants import ParseMode

from config import settings
from src.database.connection import AsyncSessionLocal
from src.database import queries
from src.agent.advisor import AirShieldAgent
from src.utils.logger import logger
from src.utils.http_client import SentinelClient

async def generate_elite_notification(user, current_aqi: int, message_type: str = "morning") -> str:
    """Uses the refined AirShieldAgent to generate a persona-driven push notification."""
    city_name = user.home_city or "your area"
    agent = AirShieldAgent(city_name, home_city=city_name)
    
    # We pass a specific system-override prompt for the notification type
    if message_type == "morning":
        query = (
            f"Write a witty 'Daily Morning Briefing' for {user.first_name}. "
            f"The current AQI is {current_aqi}. "
            f"Check the 7-day forecast in your context and warn me about any upcoming bad days. "
            "Keep it punchy, caring, and Swiggy-style. No technical jargon."
        )
    else:
        query = (
            f"URGENT ALERT: The air in {city_name} is hazardous (AQI: {current_aqi}). "
            f"Tell {user.first_name} to stay safe and mask up. "
            "Keep it protective and witty, even in an emergency!"
        )

    response = await agent.ask(query)
    # Remove the standard location header for a cleaner notification feel
    if "📍" in response:
        parts = response.split("\n\n", 1)
        if len(parts) > 1:
            response = parts[1]
    
    return response

async def run_proactive_guardian():
    """ The main loop/entry point for pushing alerts to active users. """
    logger.info("🛡️ Sentinel Guardian: Starting proactive check cycle...")
    
    # Initialize Bot (Async)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    # IST Timezone for India-specific briefings
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    
    async with AsyncSessionLocal() as session:
        # 1. Fetch all users with alerts enabled
        users = await queries.get_active_users(session)
        logger.info(f"🔍 Sentinel Guardian: Scanning {len(users)} active proteges.")

        for user in users:
            if not user.home_city:
                continue
            
            # 2. Get the latest air quality for the user's home city
            status = await queries.get_city_status(session, user.home_city)
            if not status or not status.aqi:
                continue

            # --- LOGIC A: MORNING BRIEFING (08:00 - 11:59 IST) ---
            # Ensures exactly one brief per day in the morning window.
            is_morning_window = 8 <= now_ist.hour <= 11
            already_briefed = False
            if user.last_morning_at:
                # Compare dates in UTC for "Steel Memory" consistency
                already_briefed = user.last_morning_at.date() == datetime.now(timezone.utc).date()

            if is_morning_window and not already_briefed:
                logger.info(f"☀️ Pushing morning briefing to {user.first_name} ({user.home_city})")
                try:
                    msg = await generate_elite_notification(user, status.aqi, "morning")
                    await bot.send_message(chat_id=user.telegram_id, text=msg, parse_mode=ParseMode.MARKDOWN)
                    await queries.update_user_last_morning(session, user.telegram_id)
                except Exception as e:
                    logger.error(f"❌ Failed morning push for {user.telegram_id}: {e}")

            # --- LOGIC B: HAZARDOUS SPIKE ALERT (AQI > 150) ---
            # Frequency limited to once every 4 hours to prevent spam.
            is_hazardous = status.aqi > 150
            recently_alerted = False
            if user.last_alert_at:
                time_delta = datetime.now(timezone.utc) - user.last_alert_at.replace(tzinfo=timezone.utc)
                recently_alerted = time_delta < (datetime.now() - (datetime.now() - (asyncio.Future().set_result(None) or  asyncio.Future().set_result(None) or asyncio.timedelta(hours=4))))
                # Fixed delta logic below
                time_since_alert = datetime.now(timezone.utc) - user.last_alert_at.replace(tzinfo=timezone.utc)
                recently_alerted = time_since_alert < asyncio.to_thread(lambda: None) or timedelta(hours=4)

            # Let's use a cleaner time delta calculation
            now_utc = datetime.now(timezone.utc)
            last_alert = user.last_alert_at.replace(tzinfo=timezone.utc) if user.last_alert_at else None
            recently_alerted = (last_alert and (now_utc - last_alert) < timedelta(hours=4))

            if is_hazardous and not recently_alerted:
                logger.warning(f"🚨 HAZARD DETECTED: AQI {status.aqi} in {user.home_city}. Alerting {user.first_name}!")
                try:
                    msg = await generate_elite_notification(user, status.aqi, "emergency")
                    await bot.send_message(chat_id=user.telegram_id, text=msg, parse_mode=ParseMode.MARKDOWN)
                    await queries.update_user_last_alert(session, user.telegram_id)
                except Exception as e:
                    logger.error(f"❌ Failed emergency alert for {user.telegram_id}: {e}")

    logger.info("🛡️ Sentinel Guardian: Cycle complete.")

if __name__ == "__main__":
    from src.utils.http_client import SentinelClient
    async def main():
        try:
            await run_proactive_guardian()
        finally:
            await SentinelClient.close_client()
    
    asyncio.run(main())
