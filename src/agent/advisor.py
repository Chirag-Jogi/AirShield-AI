"""
AirShield AI Advisor — Elite "Swiggy-Style" Personality 🧠🛡️
Handles intelligent health advisory using live data, ML predictions, and OpenRouter LLMs.
Features: Witty persona, Proactive Guardian logic, and RAG-lite context injection.
"""

import httpx
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from config import settings
from src.data.cities import INDIAN_CITIES
from src.data.scrapers import aqicn_scraper
from src.data.scrapers import openweather_scraper
from src.ml.predictor import predict_pm25
from src.utils.logger import logger
from src.utils.time_utils import get_ist_now
from src.utils.retry import sentinel_retry
from src.utils.http_client import get_http_client

import random

# ============================================================
# AQI CACHE — Same city ka data 5 min tak reuse karo
# Saves API calls when multiple users ask about the same city
# ============================================================
_aqi_cache: Dict[str, Dict] = {}  # {"Pune": {"data": {...}, "timestamp": 1234567890}}
AQI_CACHE_TTL = 300  # 5 minutes in seconds


def _get_cached_aqi(city_name: str) -> Optional[Dict]:
    """Returns cached AQI data if fresh (< 5 min old), else None."""
    entry = _aqi_cache.get(city_name)
    if entry and (time.time() - entry["timestamp"]) < AQI_CACHE_TTL:
        logger.info(f"[Cache] HIT for {city_name} (age: {int(time.time() - entry['timestamp'])}s)")
        return entry["data"]
    return None


def _set_cached_aqi(city_name: str, data: Dict):
    """Stores AQI data in cache with current timestamp."""
    _aqi_cache[city_name] = {"data": data, "timestamp": time.time()}


# ============================================================
# OPENROUTER KEY ROTATION — Distribute load across keys
# ============================================================
_or_key_index = 0


def _get_next_openrouter_key() -> str:
    """Round-robin rotation through all available OpenRouter keys."""
    global _or_key_index
    keys = settings.get_openrouter_keys()
    key = keys[_or_key_index % len(keys)]
    _or_key_index += 1
    return key

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
        """Builds a rich data context by fetching from BOTH APIs for accuracy."""
        city = next((c for c in INDIAN_CITIES if c.name == self.target_city), None)
        if not city:
            logger.warning(f"[Agent] Unknown city: {self.target_city}")
            self.context_data = {"error": "Unknown city"}
            return

        from src.utils.aqi_utils import calculate_us_aqi

        # 1. CHECK CACHE FIRST — avoid unnecessary API calls
        cached = _get_cached_aqi(city.name)
        if cached:
            live = cached
        else:
            # LIVE DATA FETCH — Dual-source for accuracy (parallel)
            aqicn_data = None
            ow_data = None
            try:
                aqicn_task = aqicn_scraper.fetch_air_quality(
                    settings.AQICN_API_KEY, city.name, city.aqicn_slug
                )
                ow_task = openweather_scraper.fetch_air_quality(
                    settings.OPENWEATHER_API_KEY, city.name, city.latitude, city.longitude
                )
                results = await asyncio.gather(aqicn_task, ow_task, return_exceptions=True)
                aqicn_data = results[0] if not isinstance(results[0], Exception) else None
                ow_data = results[1] if not isinstance(results[1], Exception) else None
            except Exception as e:
                logger.error(f"[Agent] Dual-fetch failed: {e}")

            # BUILD ACCURATE LIVE READING
            live = {}
            if ow_data:
                raw_pm25 = ow_data.get("pm2_5", 0)
                computed_aqi = calculate_us_aqi(raw_pm25)
                live = {
                    "aqi": computed_aqi,
                    "pm2_5_raw": round(raw_pm25, 1),
                    "source": "openweather",
                    "city": city.name,
                }
                if aqicn_data:
                    aqicn_aqi = aqicn_data.get("aqi", 0)
                    logger.info(f"[Agent] AQI Cross-check: OpenWeather={computed_aqi}, AQICN={aqicn_aqi}")
                    if aqicn_aqi > computed_aqi * 1.3:
                        live["aqi"] = max(computed_aqi, aqicn_aqi)
                        live["source"] = "cross-verified"
            elif aqicn_data:
                live = {
                    "aqi": aqicn_data.get("aqi", 0),
                    "pm2_5_raw": None,
                    "source": "aqicn",
                    "city": city.name,
                }
            else:
                live = {"aqi": 0, "pm2_5_raw": None, "source": "unavailable", "city": city.name}

            # SAVE TO CACHE
            _set_cached_aqi(city.name, live)

        # 2. ML FORECAST (Next 7 Days)
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
                "pm25": round(val, 1),
                "aqi": f_aqi,
                "is_spike": f_aqi > 100
            })

        self.context_data = {
            "current": live,
            "forecast": forecast,
            "insight": get_aqi_insight(live.get("aqi", 0)) if live else "Unknown"
        }
        self.is_initialized = True

    async def ask(self, user_query: str, chat_history: List[Dict[str, str]] = []) -> str:
        """The core interface for the 'Elite Buddy' persona."""
        # ALWAYS re-fetch fresh data on every call to avoid stale AQI/time
        await self._gather_context()

        # Build the RAG-lite Context String
        ctx = self.context_data
        cur = ctx.get("current", {})
        forecast_str = "\n".join([f"- {f['date']}: AQI {f['aqi']} (PM2.5: {f['pm25']} μg/m³)" for f in ctx.get("forecast", [])])
        
        # CRITICAL: Compute the REAL current time right before building the prompt
        now_ist = get_ist_now()
        current_time_str = now_ist.strftime("%H:%M")
        day_name = now_ist.strftime("%A")
        date_str = now_ist.strftime("%b %d, %Y")

        # Build clean AQI display for the LLM
        aqi_val = cur.get('aqi', 'N/A')
        pm25_raw = cur.get('pm2_5_raw')
        if pm25_raw is not None:
            aqi_display = f"AQI: {aqi_val} (PM2.5: {pm25_raw} μg/m³)"
        else:
            aqi_display = f"AQI: {aqi_val}"

        system_prompt = (
            f"You are **AirShield AI**, an elite, highly responsive personal health guardian.\n"
            f"The user you are currently protecting is named: **{self.user_name}**.\n"
            f"⏰ THE CURRENT TIME IS EXACTLY: **{current_time_str} IST** on **{day_name}, {date_str}**.\n"
            f"YOU MUST USE THIS EXACT TIME ({current_time_str}) IN YOUR RESPONSE HEADER. DO NOT USE ANY OTHER TIME.\n\n"
            f"[CONTEXT]\n"
            f"Target Location: {self.target_city}\n"
            f"Protected Home: {self.home_city}\n"
            f"Current {aqi_display}\n"
            f"Next 24h Trend: {ctx.get('insight')}\n"
            f"{self.target_city.upper()} 7-DAY FORECAST:\n{forecast_str}\n\n"
            f"[BEHAVIOR & TONE RULES - STRICT]\n"
            f"1. ADAPTIVE TONE:\n"
            f"   - If AQI < 100: Be energetic, witty, and use emojis like a friendly local buddy.\n"
            f"   - If AQI >= 150: Drop the jokes. Be clinical, serious, and prioritize urgent health warnings.\n"
            f"2. NO HALLUCINATIONS: You are an air quality expert, not a general doctor. Do not give medical diagnoses. If asked about the user's identity, you know they are {self.user_name}. ALWAYS respect the current day ({day_name}) and current time ({current_time_str}) when discussing forecasts.\n"
            f"3. EFFICIENCY: Keep responses under 4 sentences. Be highly scannable.\n"
            f"4. PROACTIVE: If tomorrow's forecast shows a dangerous spike (>150 AQI), you MUST mention it.\n\n"
            f"[OUTPUT FORMAT]\n"
            f"Always start with EXACTLY: '📍 **{self.target_city} | {current_time_str}**'\n"
            f"Provide your targeted insight.\n"
            f"End with '🛡️ **Guardian Tip:** [Quick 1-sentence tip]'"
        )

        messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": user_query}]
        http_client = await get_http_client()

        # ============================================================
        # SMART FALLBACK CHAIN: NVIDIA → OpenRouter Free Models
        # ============================================================

        # TIER 1: NVIDIA NIM (fastest, best quality)
        if settings.NVIDIA_API_KEY:
            nvidia_models = [
                "meta/llama-3.1-70b-instruct",
                "meta/llama-3.1-405b-instruct",
            ]
            for model in nvidia_models:
                try:
                    logger.info(f"[Agent] NVIDIA → {model}")
                    resp = await http_client.post(
                        "https://integrate.api.nvidia.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                            "Accept": "application/json"
                        },
                        json={"model": model, "messages": messages, "temperature": 0.5, "max_tokens": 1024},
                        timeout=8.0
                    )
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    logger.warning(f"[Agent] NVIDIA {model} failed: {str(e)[:80]}")
                    continue
            logger.warning("[Agent] All NVIDIA models failed. Falling back to OpenRouter...")

        # TIER 2: OpenRouter Free Models (backup, many options)
        shuffled_free = FREE_MODELS.copy()
        random.shuffle(shuffled_free)

        for model in shuffled_free[:4]:  # Try max 4 free models to avoid long waits
            api_key = _get_next_openrouter_key()
            if not api_key:
                continue
            try:
                logger.info(f"[Agent] OpenRouter → {model}")
                resp = await http_client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"model": model, "messages": messages, "temperature": 0.5, "max_tokens": 1024},
                    timeout=12.0  # Free models can be slower
                )
                resp.raise_for_status()
                result = resp.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content")
                if content:
                    return content
            except Exception as e:
                logger.warning(f"[Agent] OpenRouter {model} failed: {str(e)[:80]}")
                continue

        logger.error("[Agent] ALL models failed (NVIDIA + OpenRouter).")
        return "🛡️ Network interference! The air data is super foggy right now. Try again in 10 seconds, buddy!"

    @classmethod
    async def identify_city_async(cls, user_text: str) -> Optional[str]:
        """
        Elite City Identification with NVIDIA → OpenRouter fallback.
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

        # TIER 1: NVIDIA
        if settings.NVIDIA_API_KEY:
            for model in ["meta/llama-3.1-70b-instruct"]:
                try:
                    resp = await http_client.post(
                        "https://integrate.api.nvidia.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {settings.NVIDIA_API_KEY}", "Accept": "application/json"},
                        json={"model": model, "messages": messages, "temperature": 0, "max_tokens": 100},
                        timeout=5.0
                    )
                    resp.raise_for_status()
                    result = resp.json()["choices"][0]["message"]["content"].strip()
                    if result != "NONE" and any(c.name == result for c in INDIAN_CITIES):
                        logger.info(f"[Agent] City extracted via NVIDIA: {result}")
                        return result
                    elif result == "NONE":
                        return None
                except Exception as e:
                    logger.warning(f"[Agent City] NVIDIA failed: {str(e)[:80]}")

        # TIER 2: OpenRouter fallback
        fast_models = ["meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen-2.5-72b-instruct:free"]
        for model in fast_models:
            api_key = _get_next_openrouter_key()
            if not api_key:
                continue
            try:
                resp = await http_client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={"model": model, "messages": messages, "temperature": 0, "max_tokens": 100},
                    timeout=8.0
                )
                resp.raise_for_status()
                result = resp.json()["choices"][0]["message"]["content"].strip()
                if result != "NONE" and any(c.name == result for c in INDIAN_CITIES):
                    logger.info(f"[Agent] City extracted via OpenRouter: {result}")
                    return result
                elif result == "NONE":
                    return None
            except Exception as e:
                logger.warning(f"[Agent City] OpenRouter {model} failed: {str(e)[:80]}")
                continue

        logger.error("[Agent] ALL city extraction models failed.")
        return None
