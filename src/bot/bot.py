import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# Project tools
from src.bot import handlers
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

if __name__ == '__main__':
    # Start the health check server in a background thread for Render
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # Configure Application
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    application = ApplicationBuilder().token(TOKEN).request(request).post_shutdown(post_shutdown).build()
    
    # Register Handlers from separate module
    application.add_handler(CommandHandler('start', handlers.start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.handle_message))
    application.add_handler(CallbackQueryHandler(handlers.button_handler))
    
    print("🚀 Friendly AI Guardian is live (Elite Structure, Resilient, 24/7 Cloud Support)...")
    application.run_polling()
