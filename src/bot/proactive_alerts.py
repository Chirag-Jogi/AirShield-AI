"""
Sentinel Proactive Alerts - The Guardian System (Steel Memory Edition)
Sends daily morning briefings and real-time threshold alerts (AQI > 150)
using resilient Calendar Check logic to handle GitHub Action delays.
"""

import asyncio
import os
from datetime import datetime, timedelta
import pytz
from telegram import Bot
from dotenv import load_dotenv

from src.database.queries import (
    get_active_users, 
    get_city_status, 
    update_user_last_morning, 
    update_user_last_alert
)
from src.agent.advisor import AirShieldAgent
from src.utils.logger import logger
from src.utils.http_client import SentinelClient

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def generate_buddy_message(user, city_status, message_type="morning"):
    """Use the AI Agent to generate a punchy, Swiggy-style notification."""
    city_name = user.home_city or "your city"
    agent = AirShieldAgent(city_name, home_city=city_name)
    await agent.initialize() 

    if message_type == "morning":
        prompt = (
            f"Hey, it's morning! Give me a friendly 'Daily Briefing' for {user.first_name}. "
            f"The current AQI is {city_status.aqi}. "
            f"Use the 7-day forecast data in your context to tell them if they should expect a 'Pollution Spike' later today. "
            "Tone: Witty and caring (Swiggy/Zomato style). No raw µg/m³. No labels."
        )
    else: 
        prompt = (
            f"URGENT: The AQI in {city_name} is {city_status.aqi} (Hazardous!). "
            f"Send a quick 'Buddy Check-in' to {user.first_name} advising them to stay safe. "
            "Tone: Protective and urgent. No raw numbers except AQI status."
        )

    response = await agent.ask(prompt)
    clean_msg = response.replace(f"City: {city_name}", "").strip()
    return clean_msg

async def run_alerts():
    """Main execution loop for proactive alerts with stateful memory."""
    bot = Bot(token=TOKEN)
    users = get_active_users()
    
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    
    logger.info(f"Running proactive check for {len(users)} users (IST: {now_ist.strftime('%H:%M')})")

    for user in users:
        if not user.home_city:
            continue
            
        city_status = get_city_status(user.home_city)
        if not city_status:
            continue

        # Logic 1: Morning Briefing (8:00 AM - 11:30 AM IST)
        # Triggered once per day anytime during this window.
        is_morning_window = 8 <= now_ist.hour <= 11
        already_sent_today = False
        
        if user.last_morning_at:
            already_sent_today = user.last_morning_at.date() == datetime.utcnow().date()

        if is_morning_window and not already_sent_today:
            logger.info(f"Sending morning brief to {user.first_name} ({user.home_city})")
            try:
                msg = await generate_buddy_message(user, city_status, message_type="morning")
                await bot.send_message(chat_id=user.telegram_id, text=msg)
                update_user_last_morning(user.telegram_id)
            except Exception as e:
                logger.error(f"Failed morning brief for {user.telegram_id}: {e}")

        # Logic 2: Emergency Alert (AQI > 150)
        # Alert frequency limited to once every 4 hours.
        is_hazardous = city_status.aqi and city_status.aqi > 150
        recently_alerted = False
        
        if user.last_alert_at:
            time_since_alert = datetime.utcnow() - user.last_alert_at
            recently_alerted = time_since_alert < timedelta(hours=4)

        if is_hazardous and not recently_alerted:
            logger.warning(f"EMERGENCY: AQI {city_status.aqi} for {user.first_name}")
            try:
                msg = await generate_buddy_message(user, city_status, message_type="emergency")
                await bot.send_message(chat_id=user.telegram_id, text=msg)
                update_user_last_alert(user.telegram_id)
            except Exception as e:
                logger.error(f"Failed emergency alert for {user.telegram_id}: {e}")

    await SentinelClient.close_client()

if __name__ == "__main__":
    asyncio.run(run_alerts())
