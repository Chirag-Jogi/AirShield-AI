import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ChatAction
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# Project tools
from src.data.cities import INDIAN_CITIES
from src.database.queries import get_or_create_user, update_user_city
from src.agent.advisor import AirShieldAgent
from src.utils.http_client import SentinelClient

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Minimal server to satisfy Render's port check."""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AirShield AI is alive!")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def post_shutdown(application):
    """Clean up resources when the bot stops."""
    await SentinelClient.close_client()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    profile = get_or_create_user(user_id, first_name)
    
    if 'history' not in context.user_data:
        context.user_data['history'] = []

    if not profile.home_city:
        welcome_text = (
            f"Hi {first_name}! 🌟 Welcome to AirShield AI. I'm so glad you're here!\n\n"
            "My mission is to keep your lungs safe and help you breathe easy every day. 🌬️🛡️\n\n"
            "To get started, **which city should I keep an eye on for you?** 🏙️"
        )
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
        context.user_data['waiting_for_city'] = True
    else:
        welcome_text = (
            f"Welcome back, {first_name}! 🤗 Great to see you again.\n\n"
            f"I'm currently protecting you in **{profile.home_city}**. 🛡️\n\n"
            "What can I do for you today? Ask me anything!"
        )
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    if context.user_data.get('waiting_for_city'):
        city_name = text.strip().capitalize()
        update_user_city(user_id, city_name)
        context.user_data['waiting_for_city'] = False
        context.user_data['current_context_city'] = city_name
        
        success_message = (
            f"Got it! 🏠 From now on, I've got your back in **{city_name}**.\n\n"
            "Whenever there's a spike in pollution or a clear sky ahead, I'll be here. 🛡️🌟\n"
            "Try asking: *'Can I go for a run today?'*"
        )
        await update.message.reply_text(success_message, parse_mode="Markdown")
        return

    profile = get_or_create_user(user_id, first_name)
    target_city = None

    for city in INDIAN_CITIES:
        if city.name.lower() in text.lower():
            target_city = city.name
            break
    
    if any(k in text.lower() for k in ["my city", "home", "mine"]):
        target_city = profile.home_city

    if not target_city:
        target_city = context.user_data.get('current_context_city', profile.home_city)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.user_data['current_context_city'] = target_city 

    if 'history' not in context.user_data:
        context.user_data['history'] = []
    
    context.user_data['history'].append({"role": "user", "content": text})
    if len(context.user_data['history']) > 10:
        context.user_data['history'].pop(0)

    # --- ASYNC AGENT CALL ---
    agent = AirShieldAgent(target_city, home_city=profile.home_city)
    response = await agent.ask(text, history=context.user_data['history'][:-1]) 
    
    context.user_data['history'].append({"role": "assistant", "content": response})

    keyboard = []
    if target_city != profile.home_city:
        keyboard = [[InlineKeyboardButton(f"🏠 Make {target_city} my Home", callback_data=f"set_{target_city}")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    new_city = query.data.replace("set_", "")
    update_user_city(update.effective_user.id, new_city)
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Perfect! I'm now protecting you in **{new_city}**! 🛡️")

if __name__ == '__main__':
    # Start the health check server in a background thread for Render
    threading.Thread(target=run_health_check, daemon=True).start()
    
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    application = ApplicationBuilder().token(TOKEN).request(request).post_shutdown(post_shutdown).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 Friendly AI Guardian is live (Resilient, Async, 24/7 Cloud Support)...")
    application.run_polling()
