"""
AirShield AI Agent (Async & Resilient)
Handles intelligent health advisory using live data, ML predictions, and OpenRouter LLMs.
Follows the "AirShield Upgrade Prompt" standards: Robust, Async, and Professional.
"""

import httpx
import asyncio
import json
from datetime import datetime, timedelta

from config import settings
from src.data.cities import INDIAN_CITIES
from src.data.scrapers import openweather_scraper
from src.ml.predictor import predict_pm25
from src.utils.logger import logger
from src.utils.time_utils import get_ist_now
from src.utils.retry import sentinel_retry
from src.utils.http_client import get_http_client

# VERIFIED ULTRA-FAST FREE MODELS
FREE_MODELS = [
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "openrouter/free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free"
]

def pm25_to_aqi(pm25: float) -> tuple:
    """Convert PM2.5 to US EPA AQI (0-500 scale)."""
    breakpoints = [
        (0.0, 12.0, 0, 50, "Good 🟢"),
        (12.1, 35.4, 51, 100, "Moderate 🟡"),
        (35.5, 55.4, 101, 150, "Unhealthy (Sensitive) 🟠"),
        (55.5, 150.4, 151, 200, "Unhealthy 🔴"),
        (150.5, 250.4, 201, 300, "Very Unhealthy 🟤"),
        (250.5, 500.0, 301, 500, "Hazardous ☠️"),
    ]
    for bp_lo, bp_hi, aqi_lo, aqi_hi, label in breakpoints:
        if pm25 <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return int(aqi), label
    return 500, "Hazardous ☠️"

class AirShieldAgent:
    """Intelligent agent that generates health advice combining live data + ML + LLM."""

    def __init__(self, city_name: str, home_city: str = None):
        self.city_name = city_name
        self.home_city = home_city
        self.context = ""
        self.ready = False

    async def initialize(self):
        """Async initialization of context data."""
        city = next((c for c in INDIAN_CITIES if c.name == self.city_name), None)
        if not city or not settings.OPENWEATHER_API_KEY:
            logger.error(f"Cannot initialize agent for {self.city_name}.")
            return

        # 1. LIVE DATA (Async)
        live_data = await openweather_scraper.fetch_air_quality(
            settings.OPENWEATHER_API_KEY, city.name, city.latitude, city.longitude
        )
        if not live_data:
            return

        live_pm25 = live_data.get("pm2_5", 0)
        live_aqi, live_label = pm25_to_aqi(live_pm25)

        # 2. 7-DAY FORECAST
        predictions = []
        now = get_ist_now()
        for days_ahead in range(1, 8):
            future_date = now + timedelta(days=days_ahead)
            pred = predict_pm25(
                city=city.name, 
                hour=12, 
                month=future_date.month,
                day_of_week=future_date.weekday()
            )
            day_str = future_date.strftime("%A, %b %d")
            predictions.append(f"- {day_str}: {pred['predicted_pm25']} μg/m³")

        # 3. COMPILE CONTEXT
        self.context = (
            f"**Current Situation in {self.city_name}** ({now.strftime('%b %d')}):\n"
            f"- AQI: {live_aqi} ({live_label}), PM2.5: {live_pm25:.1f} μg/m³\n"
            f"- PM10: {live_data.get('pm10')} μg/m³, NO2: {live_data.get('no2')} μg/m³\n\n"
            f"**7-Day PM2.5 Forecast (Noon):**\n" + "\n".join(predictions)
        )
        self.ready = True
        logger.info(f"[Agent] Context initialized for {self.city_name}")

    async def ask(self, question: str, history: list = []) -> str:
        """Friendly, conversational advisor with Short-Term Memory."""
        if not self.ready:
            await self.initialize()
            if not self.ready:
                return "❌ I'm having trouble seeing the air quality right now. One moment!"

        system_prompt = (
            f"You are the AirShield AI Health Guardian—a caring and professional friend.\n"
            f"USER PROFILE: You are currently talking to someone whose HOME is **{self.home_city}**.\n"
            f"CURRENT CONTEXT: You are providing advice for **{self.city_name}**.\n\n"
            f"YOUR PERSONALITY:\n"
            f"- Polite & Respectful: Always be kind and helpful. Use a warm, human tone.\n"
            f"- Concise: Keep your reply under 120 words unless they ask for a deep dive.\n"
            f"- Context Aware: Use the history to understand 'my city' or 'tomorrow'.\n\n"
            f"ALWAYS start your response with: 📍 **City: {self.city_name}**\n\n"
            f"====== DATA CONTEXT ======\n"
            f"{self.context}\n"
            f"===========================\n"
        )

        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": question}]
        client = await get_http_client()

        @sentinel_retry(exceptions=(httpx.HTTPError, asyncio.TimeoutError))
        async def _call_api(model):
            payload = {"model": model, "messages": messages}
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        for model_name in FREE_MODELS:
            try:
                debug_name = model_name.split("/")[-1]
                logger.info(f"[Agent] Calling {debug_name}...")
                return await _call_api(model_name)
            except Exception as e:
                logger.warning(f"[Agent] {model_name} failed: {str(e)}")
                continue
                
        return "❌ I'm feeling a bit disconnected. Can we try again in a minute?"
