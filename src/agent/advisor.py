"""
AirShield AI Agent
Handles intelligent health advisory using live data, ML predictions, and OpenRouter LLMs.
"""
import requests
import json
from datetime import datetime, timedelta
import time
from src.utils.time_utils import get_ist_now

from config import settings
from src.data.cities import INDIAN_CITIES
from src.data.scrapers import openweather_scraper
from src.ml.predictor import predict_pm25
from src.utils.logger import logger
from src.utils.time_utils import get_ist_now


# VERIFIED ULTRA-FAST FREE MODELS (No 120B/405B models that take 2 minutes to reply)
FREE_MODELS = [
    "nvidia/nemotron-3-nano-30b-a3b:free",        # User requested: Fast Nemotron 30B model
    "openrouter/free",                            # Best first choice: OpenRouter auto-routes to whatever is fastest right now
    "meta-llama/llama-3.2-3b-instruct:free",      # Tiny 3B model, instantly fast
    "google/gemma-3-27b-it:free",                 # Fast 27B model
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

    def __init__(self, city_name: str):
        self.city_name = city_name
        self.context = ""
        self.live_pm25 = 0.0
        self.live_aqi = 0
        self.live_label = ""
        self.ready = False
        
        # Build context immediately
        self._build_context()

    def _build_context(self):
        """Fetch live data and generate 7-day predictions to build the LLM's reality."""
        city = next((c for c in INDIAN_CITIES if c.name == self.city_name), None)
        if not city or not settings.OPENWEATHER_API_KEY:
            logger.error(f"Cannot build context for {self.city_name}. Missing API key or city not found.")
            return

        # 1. LIVE DATA
        live_data = openweather_scraper.fetch_air_quality(
            settings.OPENWEATHER_API_KEY, city.name, city.latitude, city.longitude
        )
        if not live_data:
            return

        self.live_pm25 = live_data.get("pm2_5", 0)
        self.live_aqi, self.live_label = pm25_to_aqi(self.live_pm25)

        # 2. 7-DAY FORECAST TRANSLATION
        predictions = []
        now = get_ist_now()
        
        for days_ahead in range(1, 8):
            future_date = now + timedelta(days=days_ahead)
            # Predict for Noon (hour=12) of each future day
            pred = predict_pm25(
                city=city.name, 
                hour=12, 
                month=future_date.month,
                day_of_week=future_date.weekday(),
                # Model intelligently handles missing pollutant features (falls back to time patterns)
                no2=None, co=None, pm10=None, so2=None, o3=None, nh3=None
            )
            day_str = future_date.strftime("%A, %b %d")
            predictions.append(f"- +{days_ahead} Day(s) from today ({day_str}): Predicted PM2.5 = {pred['predicted_pm25']} μg/m³")

        # 3. COMPILE CONTEXT
        self.context = (
            f"**City Environment Context for {self.city_name}**\n\n"
            f"📌 CRITICAL TIMEFRAME: Today is {now.strftime('%A, %B %d, %Y')}. All following predictions are relative to today.\n\n"
            f"Current Actual Situation:\n"
            f"- AQI: {self.live_aqi} ({self.live_label})\n"
            f"- PM2.5: {self.live_pm25:.1f} μg/m³\n"
            f"- PM10: {live_data.get('pm10')} μg/m³\n"
            f"- NO2: {live_data.get('no2')} μg/m³\n\n"
            f"7-Day Machine Learning Forecast (Predicted PM2.5 at Noon):\n" + "\n".join(predictions)
        )
        self.ready = True
        logger.info(f"[Agent] Successfully built context for {self.city_name} with 7-day outlook.")

    def ask(self, question: str) -> str:
        """Route the user's question through the OpenRouter fallback loop."""
        if not self.ready:
            return "❌ Agent is not ready. Could not fetch live environmental data."
            
        if not settings.OPENROUTER_API_KEY:
            return "❌ OPENROUTER_API_KEY is missing from the .env file!"

        system_prompt = (
            f"You are the AirShield AI Health Advisor, a highly analytical expert in respiratory health, air pollution forecasting, and data science.\n"
            f"You receive highly accurate context about a city's current real-time air quality and the next 7 days of Machine Learning predictions.\n"
            f"Your goal is to provide deep, analytical, and practical health and scheduling advice based strictly on this data.\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"0. THE ABSOLUTE CURRENT DATE TODAY IS {get_ist_now().strftime('%A, %B %d, %Y')}. If the user asks what today's date is, you must output this exact date. Do not make up a date.\n"
            f"1. ALWAYS calculate and state the EXACT percentage change (e.g., 'PM2.5 is expected to increase by 45% tomorrow compared to today').\n"
            "2. ALWAYS mention the precise numerical values (e.g., '81.88 μg/m³').\n"
            "3. Frame your advice in terms of risk probability (e.g., 'There is a high probability of severe respiratory risk on Tuesday').\n"
            "4. Acknowledge the current date provided in the context to perfectly orient your timeline.\n"
            "5. Keep answers under 3-4 short paragraphs, use bullet points for specific advice, and be professional, analytical, yet caring.\n\n"
            f"====== DATA CONTEXT START ======\n"
            f"{self.context}\n"
            f"====== DATA CONTEXT END ======\n\n"
            "Answer the user's question with mathematical precision strictly based on the data above."
        )

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501", 
            "X-Title": "AirShield AI",               
        }

        # Try models in order until one succeeds
        for model_name in FREE_MODELS:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ]
            }
            
            # Simple retry per model in case of a temporary rate limit
            for attempt in range(2):
                try:
                    logger.info(f"[Agent] Attempting {model_name} (Try {attempt+1})...")
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=20  # Increased timeout for large language models
                    )
                    
                    # If model doesn't exist (404), stop trying this model instantly
                    if response.status_code == 404:
                        logger.error(f"[Agent] Model {model_name} not found! Skipping.")
                        break
                        
                    # If Rate Limited (429), sleep and retry
                    if response.status_code == 429:
                        logger.warning(f"[Agent] Rate limit hit on {model_name}. Waiting 3 seconds...")
                        time.sleep(3)
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    reply = data["choices"][0]["message"]["content"]
                    logger.info(f"[Agent] Success via {model_name}")
                    return f"{reply}\n\n_(Powered by {model_name})_"
                    
                except Exception as e:
                    logger.warning(f"[Agent] Error with {model_name}: {str(e)}")
                    # Brief pause before switching to completely new model
                    time.sleep(1)
                    break  # Break the attempt loop, move to next model in FREE_MODELS
                
        # If loop finishes and all failed
        logger.error("[Agent] ALL models failed or rate-limited.")
        return "❌ The AI servers are experiencing extremely high traffic right now. Please wait 1-2 minutes and ask again!"
