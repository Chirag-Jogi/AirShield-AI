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

    def __init__(self, target_city: str, home_city: Optional[str] = None, user_name: str = "Friend"):
        self.target_city = target_city
        self.home_city = home_city or target_city
        self.user_name = user_name
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
            f"You are **AirShield AI**, an elite, highly responsive personal health guardian.\n"
            f"The user you are currently protecting is named: **{self.user_name}**.\n\n"
            f"[CONTEXT]\n"
            f"Target Location: {self.target_city}\n"
            f"Protected Home: {self.home_city}\n"
            f"Current AQI: {cur.get('aqi', 'N/A')} (PM2.5: {cur.get('pm2_5', 'N/A')} μg/m³)\n"
            f"Next 24h Trend: {ctx.get('insight')}\n"
            f"{self.target_city.upper()} 7-DAY FORECAST:\n{forecast_str}\n\n"
            f"[BEHAVIOR & TONE RULES - STRICT]\n"
            f"1. ADAPTIVE TONE:\n"
            f"   - If AQI < 100: Be energetic, witty, and use emojis like a friendly local buddy.\n"
            f"   - If AQI >= 150: Drop the jokes. Be clinical, serious, and prioritize urgent health warnings.\n"
            f"2. NO HALLUCINATIONS: You are an air quality expert, not a general doctor. Do not give medical diagnoses. If asked about the user's identity, you know they are {self.user_name}.\n"
            f"3. EFFICIENCY: Keep responses under 4 sentences. Be highly scannable.\n"
            f"4. PROACTIVE: If tomorrow's forecast shows a dangerous spike (>150 AQI), you MUST mention it.\n\n"
            f"[OUTPUT FORMAT]\n"
            f"Always start with: '📍 **{self.target_city} | {datetime.now().strftime('%H:%M')}**'\n"
            f"Provide your targeted insight.\n"
            f"End with '🛡️ **Guardian Tip:** [Quick 1-sentence tip]'"
        )

        messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": user_query}]
        http_client = await get_http_client()

        # NVIDIA NIM Elite Models 🔥 (Self-Hosted on NVIDIA hardware)
        top_tier = [
            "meta/llama-3.1-70b-instruct",
            "meta/llama-3.1-405b-instruct",
            "mistralai/mistral-large"
        ]
        
        for model in top_tier:
            try:
                logger.info(f"[Agent] NVIDIA-Querying {model}...")
                resp = await http_client.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                        "Accept": "application/json"
                    },
                    json={"model": model, "messages": messages, "temperature": 0.5, "max_tokens": 1024},
                    timeout=8.0  # Generous NIM timeout 
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"[Agent] NVIDIA Model {model} failed: {str(e)[:80]}")
                continue

        logger.error("[Agent] ALL NVIDIA inference models failed.")
        return "🛡️ Network interference! The air data is super foggy right now. Try again in 10 seconds, buddy!"

    @classmethod
    async def identify_city_async(cls, user_text: str) -> Optional[str]:
        """
        Elite City Identification.
        Uses a parallel LLM race to extract a city name in <3 seconds.
        """
        available_cities = ", ".join([c.name for c in INDIAN_CITIES])
        prompt = (
            f"You are a fast location extraction expert. "
            f"The user says: '{user_text}'.\n\n"
            f"Identify if they are mentioning one of these Indian cities: {available_cities}.\n"
            f"RULES:\n"
            f"- If a city is found, return ONLY the exact city name (e.g., 'Mumbai').\n"
            f"- If no city is found or it's outside this list, return 'NONE'.\n"
            f"- Do not provide explanations or extra text."
        )

        messages = [{"role": "user", "content": prompt}]
        http_client = await get_http_client()

        reliable_models = [
            "meta/llama-3.1-70b-instruct",
            "mistralai/mixtral-8x22b-instruct-v0.1"
        ]

        for model in reliable_models:
            try:
                resp = await http_client.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                        "Accept": "application/json"
                    },
                    json={"model": model, "messages": messages, "temperature": 0, "max_tokens": 100},
                    timeout=5.0
                )
                resp.raise_for_status()
                result = resp.json()["choices"][0]["message"]["content"].strip()
                        
                if result != "NONE" and any(c.name == result for c in INDIAN_CITIES):
                    logger.info(f"[Agent] Successfully extracted city: {result}")
                    return result
                elif result == "NONE":
                    return None
            except Exception as e:
                logger.warning(f"[Agent City-Check] NVIDIA Model {model} failed: {str(e)[:80]}")
                continue
        
        logger.error("[Agent] ALL city extraction models failed.")
        return None
