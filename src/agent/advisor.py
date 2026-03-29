"""
AirShield AI Advisor — Elite "Swiggy-Style" Personality 🧠🛡️
Handles intelligent health advisory using live data, ML predictions, and OpenRouter LLMs.
Features: Witty persona, Proactive Guardian logic, and RAG-lite context injection.
"""

import httpx
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from config import settings
from src.data.cities import INDIAN_CITIES
from src.data.scrapers import openweather_scraper
from src.ml.predictor import predict_pm25
from src.utils.logger import logger
from src.utils.time_utils import get_ist_now
from src.utils.retry import sentinel_retry
from src.utils.http_client import get_http_client

import random

# ELITE FREE MODELS (Verified Active & Valid - Shuffled on every request)
FREE_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "stepfun/step-3.5-flash:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen2.5-7b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

def get_aqi_insight(aqi: int) -> str:
    """Provides a witty, persona-driven reaction to the professional AQI (0-500)."""
    if aqi <= 50: return "Lungs are singing! 🍃 Perfect for a run."
    if aqi <= 100: return "A bit hazy, but okay. Maybe skip the heavy cardio? 🏃‍♂️"
    if aqi <= 150: return "Protect those lungs, buddy. It's getting spicy out there! 👺"
    if aqi <= 200: return "Ouch. The air is basically soup right now. Mask up or stay inside! 🍲"
    if aqi <= 300: return "Hazardous. Use an air purifier or move to the moon. 🚀"
    return "EMERGENCY: The air is a literal smoke bomb. Stay indoors! 🛡️"

class AirShieldAgent:
    """
    Elite AI Guardian. 
    Combines Real-time ETL, ML Predictions, and a Witty LLM Persona.
    """

    def __init__(self, target_city: str, home_city: Optional[str] = None):
        self.target_city = target_city
        self.home_city = home_city or target_city
        self.context_data = {}
        self.is_initialized = False

    async def _gather_context(self):
        """Builds a rich data context for the LLM 'Brain'."""
        city = next((c for c in INDIAN_CITIES if c.name == self.target_city), None)
        if not city:
            logger.warning(f"[Agent] Unknown city: {self.target_city}")
            self.context_data = {"error": "Unknown city"}
            return

        # 1. LIVE DATA FETCH (Async)
        live = await openweather_scraper.fetch_air_quality(
            settings.OPENWEATHER_API_KEY, city.name, city.latitude, city.longitude
        )
        
        # 2. ML FORECAST (Next 7 Days) — Calibrated to 0-500 scale
        from src.utils.aqi_utils import calculate_us_aqi
        now = get_ist_now()
        forecast = []
        for d in range(1, 8):
            f_date = now + timedelta(days=d)
            pred = predict_pm25(
                city=city.name,
                hour=12,
                month=f_date.month,
                day_of_week=f_date.weekday()
            )
            val = pred['predicted_pm25']
            f_aqi = calculate_us_aqi(val)
            forecast.append({
                "date": f_date.strftime("%A, %b %d"),
                "pm25": val,
                "aqi": f_aqi,
                "is_spike": f_aqi > 100  # Professional 'Sensitive' Threshold
            })

        self.context_data = {
            "current": live,
            "forecast": forecast,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "insight": get_aqi_insight(live.get("aqi", 0)) if live else "Unknown"
        }
        self.is_initialized = True

    async def ask(self, user_query: str, chat_history: List[Dict[str, str]] = []) -> str:
        """The core interface for the 'Elite Buddy' persona."""
        if not self.is_initialized:
            await self._gather_context()

        # Build the RAG-lite Context String
        ctx = self.context_data
        cur = ctx.get("current", {})
        forecast_str = "\n".join([f"- {f['date']}: AQI {f['aqi']} ({f['pm25']} μg/m³)" for f in ctx.get("forecast", [])])
        
        system_prompt = (
            f"You are **AirShield AI**, the elite 24/7 personal health guardian. "
            f"You adopt a persona like a witty, caring, and tech-savvy 'Swiggy' delivery buddy. "
            f"You don't talk like a robot; you talk like someone's best friend who happens to have a PhD in Environmental Science.\n\n"
            
            f"**USER CURRENT LOCATION:** {self.target_city}\n"
            f"**USER PROTECTED HOME:** {self.home_city}\n"
            f"**LIVE DATA FOR {self.target_city.upper()} (Professional AQI 0-500 Scale):** AQI: {cur.get('aqi', 'N/A')}, PM2.5: {cur.get('pm2_5', 'N/A')}\n"
            f"**LOCAL INSIGHT:** {ctx.get('insight')}\n"
            f"**{self.target_city.upper()} 7-DAY FORECAST:**\n{forecast_str}\n\n"
            
            f"**YOUR COMMANDS:**\n"
            f"1. **City Expert**: You have live access to the city mentioned in **USER CURRENT LOCATION**. Talk about that city primarily.\n"
            f"2. **Be Witty**: Use emojis wisely. Use casual Indian English (e.g., 'buddy', 'sorted', 'solid', 'kamaal').\n"
            f"3. **Comparison (Optional)**: If the current city is different from their home, you can briefly mention if the air is better or worse than back home.\n"
            f"4. **Be Proactive**: If the forecast shows a spike (>60 μg/m³) in the next 3 days, MENTION IT, even if the user didn't ask.\n"
            f"5. **Actionable**: Always end with a punchy health tip.\n\n"
            
            f"**STRICT FORMAT:**\n"
            f"📍 **{self.target_city} | {datetime.now().strftime('%H:%M')}**\n"
            f"[Your witty response here]\n\n"
            f"🛡️ **Guardian Tip:** [Quick 1-sentence tip]"
        )

        messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": user_query}]
        http_client = await get_http_client()

        @sentinel_retry(exceptions=(httpx.HTTPError, asyncio.TimeoutError))
        async def _request_llm(model):
            resp = await http_client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                json={"model": model, "messages": messages, "temperature": 0.7},
                timeout=25.0
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        # Cascade Failover strategy (Aggressive & Shuffled)
        models_to_try = list(FREE_MODELS)
        random.shuffle(models_to_try)

        for model in models_to_try:
            try:
                logger.info(f"[Agent] Processing request with {model.split('/')[-1]}...")
                return await _request_llm(model)
            except httpx.HTTPStatusError as e:
                # Immediate failover for 429 (Busy) or 404 (Missing)
                if e.response.status_code in [429, 404]:
                    logger.warning(f"[Agent] Model {model} is busy/unavailable. Skipping immediately.")
                    continue
                logger.error(f"[Agent] Failover: {model} failed. Trying next...")
                continue
            except Exception as e:
                logger.error(f"[Agent] Failover: {model} failed. Trying next...")
                continue

        return "🛡️ AirShield is currently processing high traffic. My brain is a bit foggy—try again in a minute, buddy!"

    @classmethod
    async def identify_city_async(cls, user_text: str) -> Optional[str]:
        """
        Elite City Identification.
        Uses the LLM to extract a city name from natural language if fuzzy matching fails.
        """
        # 1. Prepare simple extraction prompt
        available_cities = ", ".join([c.name for c in INDIAN_CITIES])
        prompt = (
            f"You are a location extraction expert. "
            f"The user says: '{user_text}'.\n\n"
            f"Identify if they are mentioning one of these Indian cities: {available_cities}.\n"
            f"RULES:\n"
            f"- If a city is found, return ONLY the city name (e.g., 'Mumbai').\n"
            f"- If no city is found or it's outside this list, return 'NONE'.\n"
            f"- Do not provide explanations or extra text."
        )

        # 2. Call LLM (Ranked failover)
        messages = [{"role": "user", "content": prompt}]
        http_client = await get_http_client()

        for model in FREE_MODELS:
            try:
                resp = await http_client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                    json={"model": model, "messages": messages, "temperature": 0},
                    timeout=10.0
                )
                resp.raise_for_status()
                result = resp.json()["choices"][0]["message"]["content"].strip()
                
                if result != "NONE" and any(c.name == result for c in INDIAN_CITIES):
                    logger.info(f"[Agent] Successfully identified city: {result}")
                    return result
            except:
                continue
        
        return None
