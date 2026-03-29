"""
AirShield AI — Elite Cloud-Ready Bot Service 🛡️☁️
Powered by FastAPI + python-telegram-bot (Async).
Supports 'Stay-Awake' Webhooks for Render 24/7 reliability.
"""

import asyncio
import logging
import os
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.request import HTTPXRequest

# Project tools
from config import settings
from src.bot import handlers
from src.utils.http_client import SentinelClient
from src.utils.logger import logger

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Elite AI-driven Air Quality Guardian"
)

# Global Telegram Application Instance
tg_application = None

@app.get("/")
async def root():
    """Root endpoint for health check and 'Stay Awake' pings."""
    return {"status": "alive", "engine": "AirShield Elite Core", "env": settings.APP_ENV}

@app.get("/health")
async def health_check():
    """Formal health check endpoint for Render/uptime monitors."""
    return {"status": "healthy", "engine": "FastAPI + PTB Async"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Elite Webhook Endpoint.
    Instantly wakes up the Render service when a user sends a message!
    """
    if tg_application is None:
        return {"status": "error", "message": "Bot not initialized"}
    
    data = await request.json()
    update = Update.de_json(data, tg_application.bot)
    await tg_application.process_update(update)
    return {"status": "ok"}

async def start_telegram_bot():
    """Initialize and start the Telegram Bot based on the environment."""
    global tg_application
    
    # Configure resilient HTTPX request
    request = HTTPXRequest(
        connect_timeout=settings.CONNECT_TIMEOUT,
        read_timeout=settings.READ_TIMEOUT
    )
    
    # Build Application
    tg_application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).request(request).build()
    
    # Register Elite Handlers
    tg_application.add_handler(CommandHandler('start', handlers.start))
    tg_application.add_handler(CommandHandler('city', handlers.city_cmd))
    tg_application.add_handler(CommandHandler('settings', handlers.settings_cmd))
    tg_application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.handle_message))
    tg_application.add_handler(CallbackQueryHandler(handlers.button_handler))
    
    await tg_application.initialize()
    
    if settings.APP_ENV == "production":
        # --- WEBHOOK MODE (Elite Cloud) ---
        if not settings.WEBHOOK_URL:
            logger.error("❌ WEBHOOK_URL not set in production! Falling back to polling...")
            await tg_application.updater.start_polling()
        else:
            logger.info(f"🕸️ Setting Webhook to: {settings.WEBHOOK_URL}")
            await tg_application.bot.set_webhook(url=settings.WEBHOOK_URL)
            # We don't need updater.start_webhook() here because FastAPI handles the POST request
    else:
        # --- POLLING MODE (Local Dev) ---
        logger.info("📡 Starting Polling (Development Mode)...")
        await tg_application.updater.start_polling()
    
    await tg_application.start()
    logger.info("🚀 Friendly AI Guardian is fully synchronized and ready for the cloud.")

@app.on_event("startup")
async def startup_event():
    """Triggered when FastAPI starts."""
    asyncio.create_task(start_telegram_bot())

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global tg_application
    if tg_application:
        await tg_application.stop()
        await tg_application.shutdown()
    
    await SentinelClient.close_client()
    logger.info("🔌 System shutdown complete. All clients closed.")

if __name__ == '__main__':
    # Use environment-provided port for Render
    port = int(settings.PORT)
    uvicorn.run(app, host="0.0.0.0", port=port)
