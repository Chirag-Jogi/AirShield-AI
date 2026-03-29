"""
AirShield AI Handlers — Elite "Conversational Excellence" Edition 🛡️☁️
Refined for witty onboarding, intelligent city detection, and reactive interactions.
"""

import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from src.database.connection import AsyncSessionLocal
from src.database import queries
from src.agent.advisor import AirShieldAgent
from src.data.cities import INDIAN_CITIES
from src.utils.logger import logger
import asyncio

async def keep_typing(bot, chat_id):
    """Continuously sends the typing action until cancelled."""
    while True:
        try:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(4)  # Refresh right before Telegram's 5s expiry!
        except asyncio.CancelledError:
            break
        except Exception:
            break

def validate_city_static(city_text: str):
    """Fast, fuzzy static matching for common city inputs."""
    # Strip common punctuation that might break exact matching
    search_text = city_text.replace("?", "").replace(".", "").replace(",", "").strip().lower()
    for city in INDIAN_CITIES:
        # Match if city name is a whole word in the text (with spaces)
        if f" {city.name.lower()} " in f" {search_text} ":
            return city.name
        # Match if the exact text IS the city name
        if search_text == city.name.lower():
            return city.name
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elite Swiggy-style welcome and onboarding."""
    tg_user = update.effective_user
    async with AsyncSessionLocal() as session:
        profile = await queries.get_or_create_user(session, tg_user.id, tg_user.first_name)
        
        # Persistent Memory Sync
        try:
            context.user_data['history'] = json.loads(profile.chat_history) if profile.chat_history else []
        except:
            context.user_data['history'] = []

        if not profile.home_city:
            welcome_text = (
                f"Yo {tg_user.first_name}! 🧤 **I'm AirShield.**\n\n"
                "I'm here to watch your back (and your lungs) while you crush it 24/7. 🛡️\n\n"
                "First things first, **where are you based?** 🏙️\n"
                "(Mumbai, Delhi, Pune, Bangalore... I'm listening!)"
            )
            context.user_data['waiting_for_city'] = True
            await update.message.reply_text(welcome_text, parse_mode="Markdown")
        else:
            welcome_text = (
                f"Welcome back, {tg_user.first_name}! 🤗\n\n"
                f"Shield is up in **{profile.home_city}**. 🛡️\n"
                "What's on your mind? Ask me if it's safe to jog or if the smog is acting up!"
            )
            await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the shield's diagnostics."""
    async with AsyncSessionLocal() as session:
        profile = await queries.get_or_create_user(session, update.effective_user.id, update.effective_user.first_name)
        
        settings_text = (
            f"⚙️ **Shield Diagnostics**\n\n"
            f"👤 **Protegee**: {profile.first_name}\n"
            f"🏠 **Home City**: {profile.home_city or 'Unset (Uh oh)'}\n"
            f"🔔 **Alerts**: {'✅ Fully Optimized' if profile.is_alert_enabled else '❌ Silenced'}\n"
            f"🛡️ **Version**: 2.0 (Elite Mode Active)\n\n"
            "Wanna move? Use `/city`!"
        )
        await update.message.reply_text(settings_text, parse_mode="Markdown")

async def city_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger the relocation flow."""
    await update.message.reply_text(
        "🏙️ **Relocating the Shield...**\n\n"
        "Which city should I monitor now? Just tell me the name, I'll catch it. 📍",
        parse_mode="Markdown"
    )
    context.user_data['waiting_for_city'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """The Elite Interaction Loop — Now with AI-assisted city detection!"""
    text = update.message.text
    user_id = update.effective_user.id
    
    async with AsyncSessionLocal() as session:
        profile = await queries.get_or_create_user(session, user_id, update.effective_user.first_name)

        # -- ONBOARDING & CITY UPDATES --
        if context.user_data.get('waiting_for_city'):
            # 1. Static Validation (Fast)
            valid_city = validate_city_static(text)
            
            # 2. AI-Assisted Validation (Elite "Brain" fallback)
            if not valid_city:
                typing_task = asyncio.create_task(keep_typing(context.bot, update.effective_chat.id))
                try:
                    valid_city = await AirShieldAgent.identify_city_async(text)
                finally:
                    typing_task.cancel()

            if valid_city:
                await queries.update_user_city(session, user_id, valid_city)
                context.user_data['waiting_for_city'] = False
                context.user_data['city_retries'] = 0
                success = (
                    f"Got it! 🏠 I'm now protecting you in **{valid_city}**.\n\n"
                    "I'll shout if the PM2.5 goes through the roof. 🛡️\n"
                    "Try: *'How's the air tomorrow?'*"
                )
                await update.message.reply_text(success, parse_mode="Markdown")
            else:
                retries = context.user_data.get('city_retries', 0) + 1
                context.user_data['city_retries'] = retries
                
                if retries >= 3:
                    failure = (
                        "🚨 **Let's pause for a second!**\n\n"
                        "I really need a valid Indian city to connect to the air sensors. "
                        "If you just want to test me, please type **Delhi** or **Mumbai**. "
                        "Whenever you're ready, just tell me a city! 🏙️"
                    )
                else:
                    failure = (
                        "🏙️ Hmm, I didn't quite catch that location.\n\n"
                        "Make sure it's a major city like **Mumbai, Delhi, or Bangalore**. I'm still learning the hidden gems! 💎"
                    )
                await update.message.reply_text(failure, parse_mode="Markdown")
            return

        # -- INTELLIGENT CHAT FLOW --
        typing_task = asyncio.create_task(keep_typing(context.bot, update.effective_chat.id))
        
        try:
            # 1. Determine target city (Prioritize the ACTIVE message content)
            target_city = validate_city_static(text)
            if not target_city:
                # Elite Brain Extraction (e.g. "Gateway of India" -> "Mumbai")
                target_city = await AirShieldAgent.identify_city_async(text)
                
            # Fallback to home city if no new city is mentioned
            if not target_city:
                target_city = profile.home_city or "Mumbai"

            # 2. Agent Reasoning & Context Gathering
            # Critical: Re-initialize the agent with the NEW target city and User Identity
            history = context.user_data.get('history', [])
            agent = AirShieldAgent(target_city, home_city=profile.home_city, user_name=profile.first_name)
            response = await agent.ask(text, chat_history=history[-5:]) 
        
            # 3. Persist memory
            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": response})
            if len(history) > 10: history = history[-10:]
            context.user_data['history'] = history
            await queries.update_user_history(session, user_id, json.dumps(history))

            # 4. Dynamic UI Elements
            keyboard = []
            if target_city != profile.home_city:
                keyboard = [[InlineKeyboardButton(f"🏠 Set {target_city} as Home?", callback_data=f"set_{target_city}")]]
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
            
        finally:
            typing_task.cancel()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Home-City swap buttons."""
    query = update.callback_query
    await query.answer()
    
    new_city = query.data.replace("set_", "")
    async with AsyncSessionLocal() as session:
        await queries.update_user_city(session, update.effective_user.id, new_city)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f"✅ Done! **{new_city}** is now your primary shield zone. 🛡️",
            parse_mode="Markdown"
        )
