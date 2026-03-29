FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Final cleanup
RUN rm -rf /root/.cache/pip

# The Dockerfile is now a universal runner.
# Default to running the bot, but can be overridden as:
# docker run airshield python -m src.data.pipeline
CMD ["python", "-m", "src.bot.bot"]
