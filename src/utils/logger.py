"""
AirShield AI — Logging System
Every module uses: from src.utils.logger import logger
"""

import sys
from loguru import logger

# Remove default logger
logger.remove()

# Console logger — colorful, shows in terminal
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# File logger — saves to logs/ folder
logger.add(
    "logs/airshield_{time:YYYY-MM-DD}.log",
    rotation="1 day",      # New file every day
    retention="7 days",     # Keep logs for 7 days
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
)    