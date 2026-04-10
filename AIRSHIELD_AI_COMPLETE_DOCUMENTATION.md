# ðŸ›¡ï¸ AirShield AI â€” Complete Project Documentation

> **Version:** 2.0 | **Author:** Chirag | **Date:** April 2026
> **Project:** AirShield AI â€” The Elite 24/7 Proactive AI Guardian for Respiratory Health

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Project Folder Structure](#3-project-folder-structure)
4. [File-by-File Deep Explanation](#4-file-by-file-deep-explanation)
5. [Core Logic & Algorithms](#5-core-logic--algorithms)
6. [Execution Flow](#6-execution-flow)
7. [Integration Between Modules](#7-integration-between-modules)
8. [Error Handling & Edge Cases](#8-error-handling--edge-cases)
9. [Performance Considerations](#9-performance-considerations)
10. [Installation & Setup Guide](#10-installation--setup-guide)
11. [Testing & Validation](#11-testing--validation)
12. [Future Improvements](#12-future-improvements)
13. [Glossary](#13-glossary)

---

# 1. Project Overview

## 1.1 What is AirShield AI?

AirShield AI is a **production-grade, cloud-native MLOps platform** that transforms air quality monitoring from passive data display into **proactive health protection**. Think of it as a "Concierge for your Lungs" â€” a system that:

1. **Automatically scrapes** live pollutant data across 10+ major Indian cities every 30 minutes
2. **Predicts future pollution spikes** using an XGBoost Machine Learning model
3. **Provides personalized health advice** through a witty, caring Telegram AI Buddy powered by NVIDIA NIM (Llama 3.1 405B/70B)

In simple terms: AirShield AI watches the air so you don't have to, and warns you before things get bad.

## 1.2 What Problem Does It Solve?

Air pollution is an "invisible killer." You can't see PM2.5 particles, but they cause:
- Asthma attacks
- Heart disease
- Reduced lung capacity
- Premature death (7 million deaths/year globally per WHO)

Most air quality apps show you **what the air is like right now**. AirShield AI tells you **what it will be like tomorrow** and gives you **actionable health advice** in a conversational, friendly tone.

## 1.3 Real-World Inspiration

- **Swiggy/Zomato notification style**: The bot uses a casual, "buddy" persona instead of clinical language
- **Weather apps with forecasting**: Like AccuWeather predicts rain, AirShield predicts pollution spikes
- **Smart home health monitors**: Proactive alerts when danger is detected, not just passive displays

## 1.4 Scope and Limitations

**What AirShield AI CAN do:**
- Monitor 10 major Indian cities (Delhi, Mumbai, Bangalore, Kolkata, Chennai, Hyderabad, Pune, Ahmedabad, Lucknow, Jaipur)
- Predict PM2.5 levels for 7 days ahead
- Send morning briefings and emergency hazard alerts via Telegram
- Provide AI-powered health recommendations
- Self-evolve by retraining its ML model weekly with fresh data

**What AirShield AI CANNOT do:**
- It is NOT a medical device â€” it cannot diagnose diseases
- It cannot monitor indoor air quality (only outdoor)
- Predictions are based on historical patterns â€” unprecedented events (e.g., volcanic eruption) are not modeled
- Currently limited to Indian cities (can be extended)

---

# 2. System Architecture

## 2.1 High-Level Architecture (Explained in Words)

Imagine AirShield AI as a factory with 5 departments:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    AirShield AI System Architecture                  â”‚
â”‚                                                                     â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ EXTERNAL APIs â”‚â”€â”€â”€>â”‚ ETL PIPELINE â”‚â”€â”€â”€>â”‚ DATABASE (Supabase)  â”‚  â”‚
â”‚  â”‚ OpenWeather   â”‚    â”‚ Extract      â”‚    â”‚ PostgreSQL           â”‚  â”‚
â”‚  â”‚ AQICN         â”‚    â”‚ Transform    â”‚    â”‚ Air Quality Readings â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚ Load         â”‚    â”‚ User Profiles        â”‚  â”‚
â”‚                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                      â”‚              â”‚
â”‚                      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                â”‚              â”‚
â”‚                      â”‚ ML ENGINE    â”‚<â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â”‚
â”‚                      â”‚ XGBoost      â”‚                               â”‚
â”‚                      â”‚ Predictor    â”‚â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                    â”‚
â”‚                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜          â”‚                    â”‚
â”‚                                                v                    â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ TELEGRAM USER â”‚<â”€â”€>â”‚ AI AGENT (NVIDIA NIM LLM)               â”‚  â”‚
â”‚  â”‚ (You!)        â”‚    â”‚ + Telegram Bot Service (FastAPI)         â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                     â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ AUTOMATION: GitHub Actions (Scraper every 30min,             â”‚  â”‚
â”‚  â”‚             Retrain weekly, Heartbeat every 10min)           â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Department 1: Data Collection (ETL Pipeline)
- **What:** Every 30 minutes, GitHub Actions wakes up a cloud computer
- **How:** It runs `pipeline.py` which calls two API scrapers (OpenWeather + AQICN)
- **Result:** Fresh air quality data for 10 cities is saved to the database

### Department 2: Database (Supabase PostgreSQL)
- **What:** A cloud database that stores every air quality reading ever collected
- **How:** SQLAlchemy ORM translates Python objects into SQL rows
- **Result:** Historical data is available for ML training and user queries

### Department 3: Machine Learning Engine
- **What:** An XGBoost model trained on historical pollution data
- **How:** Takes city, hour, month, day-of-week, and pollutant levels as input
- **Result:** Predicts PM2.5 concentration for the next 7 days

### Department 4: AI Agent (Brain)
- **What:** An LLM-powered advisor that interprets data in human language
- **How:** Gathers live data + ML predictions, injects them as context into NVIDIA NIM
- **Result:** Personalized, witty health advice ("Mask up, buddy! Tomorrow's looking spicy! ðŸŒ¶ï¸")

### Department 5: Communication (Telegram Bot)
- **What:** The user-facing interface running 24/7 on Render cloud
- **How:** FastAPI handles webhooks, python-telegram-bot manages conversations
- **Result:** Users chat naturally and get instant air quality insights

## 2.2 Data Flow Between Modules

```
OpenWeather API â”€â”€â”
                  â”œâ”€â”€> pipeline.py â”€â”€> cleaner.py â”€â”€> queries.py â”€â”€> PostgreSQL DB
AQICN API â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                                      â”‚
                                                                         â”‚
User sends message â”€â”€> bot.py â”€â”€> handlers.py â”€â”€> advisor.py â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                      â”‚
                                                      â”œâ”€â”€> aqicn_scraper.py (live data)
                                                      â”œâ”€â”€> predictor.py (ML forecast)
                                                      â””â”€â”€> NVIDIA NIM API (LLM response)
                                                             â”‚
                                                             v
                                                    User receives advice
```

## 2.3 Tech Stack and WHY Each Technology Was Chosen

| Layer | Technology | WHY This Was Chosen |
|:------|:-----------|:-------------------|
| **Language** | Python 3.11 | Industry standard for ML/AI. Rich ecosystem of data science libraries |
| **Bot Interface** | python-telegram-bot | Mature async Telegram SDK. Supports webhooks for cloud deployment |
| **Web Server** | FastAPI + Uvicorn | Async-native, auto-generates API docs, handles webhooks efficiently |
| **Database ORM** | SQLAlchemy 2.0 (Async) | Industry standard. Supports both SQLite (dev) and PostgreSQL (prod) |
| **Cloud Database** | Supabase PostgreSQL | Free tier, managed PostgreSQL, perfect for production |
| **ML Framework** | XGBoost | Best-in-class for tabular data. Handles missing values natively |
| **ML Tracking** | MLflow | Tracks experiments, compares model versions, logs metrics |
| **LLM Provider** | NVIDIA NIM | Sub-5-second inference on Llama 3.1 405B. Free serverless tier |
| **HTTP Client** | HTTPX (Async) | Modern async HTTP with connection pooling. Replaces `requests` |
| **Retry Logic** | Tenacity | Production-grade retry with exponential backoff |
| **Configuration** | Pydantic Settings | Type-safe config from `.env` files with validation |
| **Logging** | Loguru | Beautiful colored logs + automatic file rotation |
| **Cloud Hosting** | Render.com | Free tier web service with webhook support |
| **Automation** | GitHub Actions | Free CI/CD. Runs cron jobs every 30 minutes |
| **Containerization** | Docker + Docker Compose | Consistent environments across dev/staging/production |
| **Testing** | Pytest + pytest-asyncio | Industry standard. Supports async test functions |

---

# 3. Project Folder Structure

## 3.1 Complete Folder Tree

```
AI_PROJECT/
â”‚
â”œâ”€â”€ .github/
â”‚   â””â”€â”€ workflows/
â”‚       â”œâ”€â”€ scrape.yml              # Automated data scraping every 30 min
â”‚       â”œâ”€â”€ retrain.yml             # Weekly ML model retraining
â”‚       â””â”€â”€ heartbeat.yml           # Keep Render service alive (ping every 10 min)
â”‚
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ raw/                        # Raw CSV datasets from Kaggle
â”‚   â”‚   â”œâ”€â”€ city_day.csv            # Daily aggregated pollution data
â”‚   â”‚   â”œâ”€â”€ city_hour.csv           # Hourly pollution (main training dataset ~65MB)
â”‚   â”‚   â”œâ”€â”€ station_day.csv         # Per-station daily data
â”‚   â”‚   â”œâ”€â”€ station_hour.csv        # Per-station hourly data (~220MB)
â”‚   â”‚   â””â”€â”€ stations.csv            # Station metadata
â”‚   â”œâ”€â”€ processed/
â”‚   â”‚   â””â”€â”€ city_hour_clean.csv     # Cleaned dataset ready for ML (~44MB)
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â””â”€â”€ xgboost_pm25.joblib     # Trained XGBoost model artifact (~1.3MB)
â”‚   â”œâ”€â”€ airshield.db                # Local SQLite database (development)
â”‚   â””â”€â”€ mlflow.db                   # MLflow experiment tracking database
â”‚
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ __init__.py                 # Marks src as a Python package
â”‚   â”‚
â”‚   â”œâ”€â”€ agent/                      # AI Brain â€” LLM-powered health advisor
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ advisor.py              # Core AI agent with persona & context injection
â”‚   â”‚   â””â”€â”€ test_advisor_fix.py     # Quick test script for the advisor
â”‚   â”‚
â”‚   â”œâ”€â”€ bot/                        # Telegram Bot â€” User-facing interface
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ bot.py                  # FastAPI + Telegram bot startup & webhook
â”‚   â”‚   â”œâ”€â”€ handlers.py             # Message handlers, city detection, chat flow
â”‚   â”‚   â””â”€â”€ proactive_alerts.py     # Morning briefings & emergency hazard alerts
â”‚   â”‚
â”‚   â”œâ”€â”€ data/                       # Data Engineering â€” ETL pipeline
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ cities.py               # City configuration (coordinates, slugs)
â”‚   â”‚   â”œâ”€â”€ cleaner.py              # Data normalization & consensus engine
â”‚   â”‚   â”œâ”€â”€ historical_cleaner.py   # Kaggle dataset cleaning for ML training
â”‚   â”‚   â”œâ”€â”€ historical_loader.py    # Bulk load cleaned CSV into database
â”‚   â”‚   â”œâ”€â”€ pipeline.py             # Main ETL orchestrator
â”‚   â”‚   â””â”€â”€ scrapers/
â”‚   â”‚       â”œâ”€â”€ __init__.py
â”‚   â”‚       â”œâ”€â”€ openweather_scraper.py   # OpenWeatherMap API scraper (async)
â”‚   â”‚       â””â”€â”€ aqicn_scraper.py         # AQICN API scraper (async)
â”‚   â”‚
â”‚   â”œâ”€â”€ database/                   # Database Layer â€” ORM & queries
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ connection.py           # Async engine, session factory, DB init
â”‚   â”‚   â”œâ”€â”€ models.py               # SQLAlchemy table schemas
â”‚   â”‚   â””â”€â”€ queries.py              # All database read/write operations
â”‚   â”‚
â”‚   â”œâ”€â”€ ml/                         # Machine Learning â€” Prediction engine
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ feature_engineering.py  # Transform raw data into ML features
â”‚   â”‚   â”œâ”€â”€ model_comparison.py     # Compare 4 ML models, pick the best
â”‚   â”‚   â”œâ”€â”€ predictor.py            # Singleton model loader & prediction API
â”‚   â”‚   â”œâ”€â”€ train_model.py          # Initial XGBoost training pipeline
â”‚   â”‚   â””â”€â”€ train_continuous.py     # Self-evolution: retrain from live data
â”‚   â”‚
â”‚   â””â”€â”€ utils/                      # Shared Utilities
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ aqi_utils.py            # US EPA AQI calculation from PM2.5
â”‚       â”œâ”€â”€ http_client.py          # Singleton async HTTP client (HTTPX)
â”‚       â”œâ”€â”€ logger.py               # Loguru logging configuration
â”‚       â”œâ”€â”€ retry.py                # Tenacity-based retry decorator
â”‚       â””â”€â”€ time_utils.py           # IST timezone & naive UTC conversion
â”‚
â”œâ”€â”€ tests/                          # Automated Test Suite
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ test_pipeline.py            # ETL pipeline integration tests
â”‚   â””â”€â”€ test_data_engine.py         # Data cleaner & consensus tests
â”‚
â”œâ”€â”€ notebooks/
â”‚   â””â”€â”€ 01_eda.ipynb                # Exploratory Data Analysis notebook
â”‚
â”œâ”€â”€ logs/                           # Auto-generated log files (daily rotation)
â”œâ”€â”€ mlruns/                         # MLflow experiment artifacts
â”œâ”€â”€ venv/                           # Python virtual environment
â”‚
â”œâ”€â”€ config.py                       # Central configuration (Pydantic Settings)
â”œâ”€â”€ spin_airshield.py               # Interactive CLI dashboard & control center
â”œâ”€â”€ requirements.txt                # Python dependencies
â”œâ”€â”€ Dockerfile                      # Docker container definition
â”œâ”€â”€ docker-compose.yml              # Multi-container orchestration
â”œâ”€â”€ render.yaml                     # Render.com deployment blueprint
â”œâ”€â”€ .env                            # Secret API keys (NOT in git)
â”œâ”€â”€ .env.example                    # Template showing required secrets
â”œâ”€â”€ .gitignore                      # Files excluded from version control
â”œâ”€â”€ .dockerignore                   # Files excluded from Docker builds
â”œâ”€â”€ README.md                       # Project overview and setup instructions
â””â”€â”€ MASTER_CLASS_DOCS.md            # Previous documentation version
```

## 3.2 Detailed Explanation of Each Folder

### `.github/workflows/` â€” The Automation Layer
**Purpose:** Contains YAML files that tell GitHub's cloud servers what to do on a schedule.
**Why it exists:** Without this, someone would need to manually run the scraper every 30 minutes. GitHub Actions automates this for free.
**What it contains:** Three workflow files â€” one for scraping data, one for retraining the ML model, and one for keeping the Render service alive.

### `data/` â€” The Storage Layer
**Purpose:** Holds all persistent data files â€” raw CSVs, cleaned datasets, trained ML models, and databases.
**Why it exists:** ML models need historical data to learn patterns. This folder is the "memory" of the entire system.

- **`data/raw/`** â€” Original Kaggle datasets (city_hour.csv has ~1.3 million rows of hourly pollution data from 2015-2020)
- **`data/processed/`** â€” Cleaned version of the data with outliers removed and missing values handled
- **`data/models/`** â€” Serialized ML model files (`.joblib` format) that can be loaded instantly for predictions
- **`data/airshield.db`** â€” Local SQLite database used during development (production uses Supabase PostgreSQL)
- **`data/mlflow.db`** â€” MLflow tracking database that records every training experiment

### `src/` â€” The Engine Room
**Purpose:** The core Python package containing ALL business logic, organized into sub-packages by responsibility.
**Why it exists:** Clean separation of concerns. Each sub-package handles one aspect of the system.

### `tests/` â€” Quality Assurance
**Purpose:** Automated tests that verify the system works correctly after every code change.
**Why it exists:** Without tests, you can't confidently deploy new features â€” you might break existing functionality.

### `notebooks/` â€” The Laboratory
**Purpose:** Jupyter notebooks for exploratory data analysis (EDA) â€” understanding the data before building models.
**Why it exists:** Before writing production code, data scientists explore data visually to find patterns, outliers, and correlations.

### `logs/` â€” The Black Box
**Purpose:** Stores daily log files recording every action the system takes.
**Why it exists:** If the system crashes at 3 AM, these logs tell you exactly what happened and why.

---

# 4. File-by-File Deep Explanation

## 4.1 Root Configuration Files

---

### ðŸ“„ `config.py` â€” Central Configuration Hub

**Role:** The single source of truth for ALL settings. Every module imports `from config import settings`.

**Full Code Breakdown:**

```python
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent
```

- `Path(__file__)` gets the path to this file (`config.py`)
- `.resolve()` converts it to an absolute path (e.g., `C:\Users\Chirag\...\AI_PROJECT\config.py`)
- `.parent` gets the directory containing this file (the project root)
- **Why:** All other paths (data/, logs/, models/) are built relative to this. Works on Windows, Linux, and Docker.

```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "AirShield AI"
    PROJECT_VERSION: str = "0.1.0"
```

- `BaseSettings` from Pydantic automatically reads values from environment variables and `.env` files
- If `PROJECT_NAME` is set in `.env`, it overrides `"AirShield AI"`. Otherwise, the default is used.
- **Why Pydantic:** It validates types automatically. If someone puts `PORT=abc` in `.env`, Pydantic will crash immediately with a clear error instead of failing silently later.

```python
    DATABASE_URL: str = Field(
        default=f"sqlite:///{BASE_DIR / 'data' / 'airshield.db'}",
        description="SQLAlchemy-compatible database URL"
    )
```

- Default is a local SQLite database file â€” works "out of the box" without any setup
- In production, this is overridden by a Supabase PostgreSQL URL from `.env`
- `Field()` adds metadata (description) for documentation purposes

```python
    OPENROUTER_API_KEYS: str = Field(default="", description="Comma-separated OpenRouter keys")
```

- Supports **multi-key pooling**: multiple API keys separated by commas
- If one key hits rate limits, the system can rotate to another
- **Why:** Free API tiers have low rate limits. Multiple keys multiply your capacity.

```python
    API_MAX_RETRIES: int = 3
    API_RETRY_DELAY: float = 2.0
    CONNECT_TIMEOUT: float = 30.0
    READ_TIMEOUT: float = 30.0
```

- Configurable retry behavior â€” retry 3 times with 2-second base delay
- 30-second timeouts prevent the system from hanging on slow APIs
- **Why configurable:** In development you want fast failures; in production you want patience.

```python
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

- Tells Pydantic: "Read the `.env` file at project root"
- `extra="ignore"`: If `.env` has variables we didn't define (e.g., `RANDOM_VAR=123`), don't crash â€” just ignore them

```python
    def ensure_directories(self):
        for dir_path in [self.DATA_DIR, self.RAW_DATA_DIR,
                         self.PROCESSED_DATA_DIR, self.MODELS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
```

- Creates `data/`, `data/raw/`, `data/processed/`, `data/models/` if they don't exist
- `parents=True`: Creates intermediate directories too
- `exist_ok=True`: Don't crash if the directory already exists
- **Why:** Prevents "FileNotFoundError" on first run

```python
    def get_openrouter_keys(self) -> list[str]:
        keys = []
        if self.OPENROUTER_API_KEYS:
            keys = [k.strip() for k in self.OPENROUTER_API_KEYS.split(",") if k.strip()]
        if not keys and self.OPENROUTER_API_KEY:
            keys = [self.OPENROUTER_API_KEY]
        return keys if keys else [""]
```

- Splits comma-separated keys into a list
- Falls back to single key if multi-key string is empty
- Returns `[""]` as last resort so the code doesn't crash on empty iteration

```python
settings = Settings()
settings.ensure_directories()
```

- These two lines run **when any file imports config** â€” the Settings object is created once and reused everywhere (Singleton pattern)

**How it connects to other files:** Every single module in the project does `from config import settings` to get API keys, database URLs, paths, and retry settings.

---

### ðŸ“„ `spin_airshield.py` â€” Interactive CLI Dashboard

**Role:** A manual control center for developers. Provides a menu-driven interface to trigger individual system components.

**Key Functions:**

| Function | Purpose | What It Triggers |
|:---------|:--------|:----------------|
| `run_data_pipeline()` | Manually trigger ETL | `src.data.pipeline.run_pipeline_async()` |
| `run_proactive_guardian()` | Test proactive alerts | `src.bot.proactive_alerts.run_proactive_guardian()` |
| `run_self_evolution()` | Retrain ML model | `src.ml.train_continuous.train_and_track()` |
| `launch_bot_service()` | Start the Telegram bot | `python -m src.bot.bot` (subprocess) |
| `main_menu()` | Interactive menu loop | Displays options 1-5 and routes to above functions |

**Design Detail â€” Rich Library:**
```python
try:
    from rich.console import Console
    has_rich = True
except ImportError:
    has_rich = False
```
- Uses `rich` library for colorful, formatted terminal output
- Falls back to plain `print()` if `rich` is not installed
- Auto-installs `rich` on first run if missing

**How it connects:** This is a developer tool â€” it imports and calls functions from `pipeline.py`, `proactive_alerts.py`, `train_continuous.py`, and launches `bot.py` as a subprocess.

---

*Continued in subsequent sections for all remaining files...*
# AirShield AI â€” Documentation Part 2
# File-by-File Deep Explanation (Continued) & Chapters 5â€“8

---

## 4.2 Utilities Module (`src/utils/`)

---

### ðŸ“„ `src/utils/logger.py` â€” Centralized Logging

**Role:** Configures the Loguru logging library for the entire application. Every module uses `from src.utils.logger import logger`.

```python
from loguru import logger

logger.remove()  # Remove default handler
```
- Loguru ships with a default handler. We remove it to set our own custom format.

```python
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)
```
- **Console handler**: Shows colorful, timestamped messages in the terminal
- `level="INFO"`: Only shows INFO and above (not DEBUG noise)
- Format breakdown: `09:45:12 | INFO     | src.data.pipeline - âœ… Pipeline complete`

```python
logger.add(
    "logs/airshield_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
)
```
- **File handler**: Saves ALL messages (including DEBUG) to daily log files
- `rotation="1 day"`: New file every day (e.g., `airshield_2026-04-09.log`)
- `retention="7 days"`: Auto-deletes log files older than 7 days

**Why this design:** Console shows only important info (so it's readable). Files capture everything (for post-mortem debugging).

---

### ðŸ“„ `src/utils/time_utils.py` â€” Timezone Handling

**Role:** Provides consistent time handling across the entire system.

```python
def get_ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)
```
- Returns current time in **Indian Standard Time (IST = UTC+5:30)**
- Cloud servers (GitHub Actions, Render) run on UTC
- Without this, a reading at 10 PM in Delhi would display as 4:30 PM
- **Used by:** `advisor.py` (day/date awareness), `predictor.py` (auto-detect hour/month)

```python
def to_naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt
```
- Converts any datetime to **"naive UTC"** (no timezone label)
- **Why:** PostgreSQL's `TIMESTAMP WITHOUT TIME ZONE` column type requires naive datetimes. If you send a timezone-aware datetime, asyncpg will throw an error.
- **Used by:** `queries.py` when saving records and updating user timestamps

---

### ðŸ“„ `src/utils/retry.py` â€” Resilient Retry Decorator

**Role:** Wraps API calls with automatic retry + exponential backoff using the Tenacity library.

```python
def sentinel_retry(
    max_attempts: int = None,
    exceptions: tuple = (Exception,),
    base_delay: float = None,
    max_delay: float = 10.0
):
```
- **Parameters:**
  - `max_attempts`: How many times to retry (default: 3 from config)
  - `exceptions`: Which error types trigger a retry
  - `base_delay`: Initial wait time (default: 2.0s from config)
  - `max_delay`: Maximum wait between retries (caps at 10s)

```python
    return retry(
        stop=stop_after_attempt(_max_attempts),
        wait=wait_exponential(multiplier=_base_delay, max=max_delay),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True
    )
```
- `stop_after_attempt(3)`: Give up after 3 tries
- `wait_exponential(multiplier=2.0)`: Wait 2s, then 4s, then 8s (capped at 10s)
- `retry_if_exception_type`: Only retry on specified exceptions (not all errors)
- `before_sleep`: Log a WARNING before each retry sleep
- `reraise=True`: After all retries fail, raise the original exception

**Example usage:**
```python
@sentinel_retry(exceptions=(httpx.HTTPError, asyncio.TimeoutError))
async def fetch_air_quality(api_key, city_name, city_slug):
    ...
```
If the AQICN API returns an HTTP error, the function automatically retries 3 times before giving up.

---

### ðŸ“„ `src/utils/http_client.py` â€” Global HTTP Connection Pool

**Role:** Provides a singleton async HTTP client to prevent socket exhaustion.

```python
class SentinelClient:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(20.0, connect=10.0),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                follow_redirects=True
            )
        return cls._client
```
- **Singleton pattern**: Only ONE client exists for the entire application
- **Why:** Creating a new HTTP client per request wastes resources and can exhaust OS sockets
- `max_connections=100`: Up to 100 simultaneous connections
- `max_keepalive_connections=20`: Keep 20 connections alive for reuse
- `follow_redirects=True`: Automatically follow HTTP 301/302 redirects

```python
    @classmethod
    async def close_client(cls):
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            cls._client = None
```
- Clean shutdown during app exit to prevent resource leaks
- Called in `bot.py`'s shutdown event

**How it connects:** Used by `openweather_scraper.py`, `aqicn_scraper.py`, and `advisor.py` for all HTTP requests.

---

### ðŸ“„ `src/utils/aqi_utils.py` â€” AQI Calculation Engine

**Role:** Converts raw PM2.5 concentration (Î¼g/mÂ³) into the standard US EPA Air Quality Index (0-500 scale).

```python
def calculate_us_aqi(pm25: float) -> int:
    breakpoints = [
        (0.0, 12.0, 0, 50),       # Good
        (12.1, 35.4, 51, 100),    # Moderate
        (35.5, 55.4, 101, 150),   # Unhealthy for Sensitive Groups
        (55.5, 150.4, 151, 200),  # Unhealthy
        (150.5, 250.4, 201, 300), # Very Unhealthy
        (250.5, 350.4, 301, 400), # Hazardous
        (350.5, 500.4, 401, 500), # Hazardous+
    ]
```
- Each tuple: `(C_low, C_high, I_low, I_high)` â€” PM2.5 concentration range maps to AQI range
- **Formula (US EPA Linear Interpolation):**
  ```
  AQI = ((I_high - I_low) / (C_high - C_low)) Ã— (C - C_low) + I_low
  ```
- **Example:** PM2.5 = 25.0 Î¼g/mÂ³
  - Falls in (12.1, 35.4, 51, 100) â€” "Moderate" range
  - AQI = ((100-51)/(35.4-12.1)) Ã— (25.0-12.1) + 51 = **78**

**Why this exists:** OpenWeatherMap returns raw PM2.5 concentrations, not AQI values. AQICN returns AQI directly. This function standardizes everything to one scale.

---

## 4.3 Data Engineering Module (`src/data/`)

---

### ðŸ“„ `src/data/cities.py` â€” City Configuration Registry

**Role:** Single source of truth for all monitored cities with coordinates and API slugs.

```python
@dataclass(frozen=True)
class CityConfig:
    name: str
    latitude: float
    longitude: float
    aqicn_slug: str
```
- `@dataclass(frozen=True)` makes instances immutable (can't accidentally change Delhi's coordinates)
- `aqicn_slug`: The URL-friendly identifier used by AQICN API (e.g., "bangalore" not "Bengaluru")

```python
INDIAN_CITIES: list[CityConfig] = [
    CityConfig("Delhi", 28.6139, 77.2090, "delhi"),
    CityConfig("Mumbai", 19.0760, 72.8777, "mumbai"),
    # ... 8 more cities
]
```
- **Why centralized:** Both scrapers, the predictor, the advisor, and the handlers all import from here. Adding a new city means changing ONE file.

---

### ðŸ“„ `src/data/scrapers/openweather_scraper.py` â€” OpenWeatherMap Scraper

**Role:** Fetches live air quality data from OpenWeatherMap API for all configured cities.

**Key Function: `fetch_air_quality()`**
```python
@sentinel_retry(exceptions=(httpx.HTTPError, asyncio.TimeoutError))
async def fetch_air_quality(api_key, city_name, lat, lon) -> dict | None:
```
- **Input:** API key, city name, latitude, longitude
- **Output:** Dictionary with standardized air quality data
- **Decorated with:** `@sentinel_retry` for automatic retries on network failures

**Internal Logic:**
1. Calls `http://api.openweathermap.org/data/2.5/air_pollution` with coordinates
2. Extracts pollutant components (PM2.5, PM10, CO, NO2, O3, SO2, NH3)
3. **Critical step:** Converts PM2.5 to real 0-500 AQI using `calculate_us_aqi()`
4. Returns standardized dictionary with timestamp in UTC ISO format

**Key Function: `fetch_all_cities_async()`**
```python
async def fetch_all_cities_async(api_key) -> list[dict]:
    semaphore = asyncio.Semaphore(10)
```
- Uses `asyncio.Semaphore(10)` to limit concurrent requests to 10
- **Why:** Without the semaphore, all 10 cities would hit the API simultaneously, risking rate limits
- Uses `asyncio.gather()` for concurrent (not sequential) execution â€” 10x faster than sequential

---

### ðŸ“„ `src/data/scrapers/aqicn_scraper.py` â€” AQICN Scraper

**Role:** Secondary data source from World Air Quality Index project. Provides production-grade AQI values.

**Key differences from OpenWeather scraper:**
- Uses AQICN's `city_slug` instead of coordinates: `https://api.waqi.info/feed/{city_slug}/`
- AQICN returns AQI directly (no conversion needed)
- AQICN provides geographic coordinates in the response

**Why two scrapers:** Redundancy. If OpenWeatherMap goes down, AQICN keeps the system alive. The pipeline runs both concurrently and uses the "Fattest Dataset" consensus strategy.

---

### ðŸ“„ `src/data/cleaner.py` â€” Data Normalization & Consensus Engine

**Role:** Normalizes multi-source data and resolves conflicts when multiple sources report for the same city.

**Function 1: `clean_reading(data)`**
1. **Mandatory field validation:** Rejects records missing city, latitude, longitude, aqi, or timestamp
2. **AQI normalization:** Converts OpenWeather's 1-5 scale to US EPA 0-500 using a lookup table:
   ```python
   OPENWEATHER_TO_EPA = {1: 25, 2: 75, 3: 125, 4: 175, 5: 250}
   ```
3. **Outlier clamping:** If AQI > 500 (impossible), clamps to 500. If < 0, clamps to 0.
4. **Pollutant sanitization:** Sets negative pollutant values to None, ensures all pollutant keys exist

**Function 2: `resolve_consensus(readings)` â€” "Fattest Dataset" Strategy**
- Groups readings by city
- If only one source reports for a city, use it directly
- If multiple sources report, pick the one with the **most non-None pollutant values**
- **Why:** The source with more data points is more reliable and useful for ML predictions

**Function 3: `clean_and_resolve(readings)` â€” Entry Point**
- Step 1: Clean each individual reading
- Step 2: Run consensus resolution across sources
- Returns the final list of validated, de-duplicated readings

---

### ðŸ“„ `src/data/pipeline.py` â€” ETL Orchestrator

**Role:** The master controller for the entire Extract-Transform-Load process.

**Class: `PipelineResult`**
```python
@dataclass
class PipelineResult:
    sources_attempted: int = 0
    sources_succeeded: int = 0
    raw_readings: int = 0
    resolved_readings: int = 0
    saved_readings: int = 0
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
```
- Structured observability object â€” tracks every metric of the pipeline run
- `success` property: Returns True only if at least one source succeeded and readings were saved

**Function: `run_pipeline_async()`**
1. **EXTRACT:** Creates concurrent tasks for OpenWeather + AQICN scrapers
   ```python
   raw_results = await asyncio.gather(*extraction_tasks)
   ```
   Both scrapers run simultaneously, not sequentially.

2. **TRANSFORM:** Passes all raw readings through `clean_and_resolve()`
3. **LOAD:** Opens an async database session and calls `queries.save_readings()`
4. **Report:** Logs comprehensive metrics (sources, readings, duration)

**Fault isolation:** If one scraper fails, the other's data still gets saved. The pipeline never crashes completely.

---

### ðŸ“„ `src/data/historical_cleaner.py` â€” Kaggle Dataset Cleaner

**Role:** Cleans the raw `city_hour.csv` Kaggle dataset (~1.3M rows) for ML training.

**Pipeline steps:**
1. `load_raw_data()` â€” Load the 65MB CSV
2. Standardize city names (`Bengaluru â†’ Bangalore`)
3. `drop_unused_columns()` â€” Remove Benzene, Toluene, Xylene (not available from live APIs)
4. `remove_outliers()` â€” Delete rows where AQI > 500, PM2.5 > 500, PM10 > 600
5. `handle_missing_values()` â€” Drop rows where BOTH PM2.5 and AQI are missing (keep others â€” XGBoost handles NaN natively)
6. Save cleaned data to `data/processed/city_hour_clean.csv`

---

### ðŸ“„ `src/data/historical_loader.py` â€” Database Bulk Loader

**Role:** Loads the cleaned CSV into the SQLite/PostgreSQL database in batches of 5,000 rows.

**Why batch loading:** Inserting 300K rows one-by-one takes ~30 minutes. Batches of 5,000 take ~30 seconds.

---

## 4.4 Database Module (`src/database/`)

### ðŸ“„ `src/database/connection.py` â€” Async Database Engine

**Role:** Creates the async SQLAlchemy engine and session factory.

**Key design: Protocol mapping**
```python
if db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif "postgres" in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
```
- SQLAlchemy needs specific driver prefixes for async operation
- SQLite â†’ aiosqlite driver, PostgreSQL â†’ asyncpg driver
- **"Giga-Sledgehammer" fix:** Disables prepared statement caching for PgBouncer compatibility

### ðŸ“„ `src/database/models.py` â€” Table Schemas

**Table 1: `AirQualityReading`** â€” Each row = one air quality snapshot
- `id` (Integer, auto-increment) â€” Unique row identifier
- `city` (String, indexed) â€” City name with index for fast queries
- `latitude/longitude` (Float) â€” GPS coordinates
- `aqi` (Integer) â€” Air Quality Index (0-500)
- `pm2_5, pm10, co, no, no2, o3, so2, nh3` (Float) â€” Individual pollutant concentrations
- `measured_at` (DateTime) â€” When pollution was measured
- `created_at` (DateTime) â€” When record was saved to database
- `source` (String) â€” Data origin ("openweathermap", "aqicn", "kaggle_historical")

**Table 2: `User`** â€” Telegram user profiles
- `telegram_id` (BigInteger, primary key) â€” Telegram's unique user ID
- `first_name` (String) â€” User's display name
- `home_city` (String) â€” Registered home city for monitoring
- `is_alert_enabled` (Boolean) â€” Whether proactive alerts are on
- `last_morning_at` (DateTime) â€” Prevents duplicate morning briefings ("Steel Memory")
- `last_alert_at` (DateTime) â€” Prevents alert spam (max once per 4 hours)
- `chat_history` (String) â€” JSON-serialized conversation history for memory

### ðŸ“„ `src/database/queries.py` â€” All Database Operations

Key functions:
- `save_readings()` â€” Saves air quality readings with per-record fault tolerance
- `get_city_status()` â€” Gets latest reading for a city (used by proactive alerts)
- `get_or_create_user()` â€” Upsert pattern for Telegram users
- `update_user_city()` â€” Changes user's monitored city
- `update_user_last_morning()` / `update_user_last_alert()` â€” "Steel Memory" timestamp updates
- `update_user_history()` â€” Persists chat history to cloud database

---

## 4.5 Machine Learning Module (`src/ml/`)

### ðŸ“„ `src/ml/feature_engineering.py` â€” Feature Preparation

**Role:** Transforms raw datetime + city data into ML-ready numeric features.

**Features created:**
| Feature | Source | Why It Matters |
|:--------|:-------|:--------------|
| `hour` (0-23) | From timestamp | Pollution peaks at 7-9 AM and 9-11 PM (rush hour) |
| `month` (1-12) | From timestamp | Winter months (Nov-Feb) have worst pollution |
| `day_of_week` (0-6) | From timestamp | Weekday traffic differs from weekend |
| `is_winter` (0/1) | Derived from month | Temperature inversions trap pollutants in winter |
| `city_code` (0-9) | Encoded from city name | Each city has different pollution baseline |
| `NO, NO2, CO, SO2, O3, NH3, PM10` | Raw pollutants | Correlated predictors for PM2.5 |

### ðŸ“„ `src/ml/predictor.py` â€” Singleton Prediction Engine

**Key design: Singleton model loading**
```python
_MODEL_CACHE = {}

def get_model(filename="xgboost_pm25.joblib"):
    if filename not in _MODEL_CACHE:
        _MODEL_CACHE[filename] = joblib.load(filepath)
    return _MODEL_CACHE[filename]
```
- Loads the 1.3MB model file from disk ONCE, keeps it in memory
- Subsequent calls skip disk I/O entirely
- **Why:** The advisor generates 7-day forecasts (7 prediction calls). Without caching, each call re-reads the file.

**`predict_pm25()` function:**
1. Auto-detects current hour/month/day-of-week from IST time (or accepts manual overrides)
2. Maps city name to numeric code
3. Builds a feature DataFrame matching training format
4. Calls `model.predict()` and clamps result to 0-550 range

### ðŸ“„ `src/ml/train_model.py` â€” Initial Training Pipeline

XGBoost hyperparameters explained:
- `n_estimators=200`: Build 200 decision trees
- `max_depth=6`: Each tree can ask 6 questions deep (prevents overfitting)
- `learning_rate=0.1`: Each tree corrects 10% of the previous trees' errors
- `subsample=0.8`: Each tree sees 80% of the data (prevents memorization)
- `colsample_bytree=0.8`: Each tree sees 80% of features

### ðŸ“„ `src/ml/train_continuous.py` â€” Self-Evolution Engine

**Role:** Automatically retrains the model on fresh live data from the production database.

**Champion vs. Challenger Guardrail:**
```python
if r2 >= 0.70:
    logger.info("ðŸ† Model Evolved! Promoting Challenger to Champion.")
    joblib.dump(model, current_model_path)
```
- New model must achieve RÂ² â‰¥ 0.70 to replace the current one
- If accuracy is below threshold, the old model stays in production
- All experiments are tracked in MLflow for audit trail

### ðŸ“„ `src/ml/model_comparison.py` â€” Model Tournament

Compares 4 algorithms on the same dataset:
1. Linear Regression (baseline)
2. Random Forest
3. XGBoost â† **Winner** (RÂ² ~0.77)
4. LightGBM

Saves the winning model and a CSV summary of all results.

---

## 4.6 AI Agent Module (`src/agent/`)

### ðŸ“„ `src/agent/advisor.py` â€” The AI Brain

**Class: `AirShieldAgent`**

```python
def __init__(self, target_city, home_city=None, user_name="Friend"):
```
- Each conversation creates a new agent instance with the user's context
- `target_city`: The city being asked about (may differ from home city)
- `user_name`: Injected into LLM prompt for personalized responses

**`_gather_context()` â€” Context Builder**
1. Looks up city coordinates from `INDIAN_CITIES`
2. Calls AQICN scraper for live AQI data
3. Generates 7-day forecast using `predict_pm25()` for each day at noon
4. Converts PM2.5 predictions to AQI using `calculate_us_aqi()`
5. Marks any day with AQI > 100 as a "spike"

**`ask()` â€” Core LLM Interface**
1. Builds a detailed system prompt with:
   - User identity (name, home city)
   - Current date and day name (prevents day-of-week hallucinations)
   - Live AQI data
   - 7-day forecast
   - Behavior rules (be witty when safe, be serious when hazardous)
2. Sends to NVIDIA NIM API (tries 3 models in sequence: Llama 70B â†’ 405B â†’ Mistral Large)
3. Returns the LLM's response text

**`identify_city_async()` â€” AI City Detection**
- Used when a user types something like "How's the air near Gateway of India?"
- Sends to LLM with a list of valid cities
- LLM extracts "Mumbai" from the context
- Returns the exact city name or None

---

## 4.7 Bot Module (`src/bot/`)

### ðŸ“„ `src/bot/bot.py` â€” Application Entry Point

**Architecture: FastAPI + Telegram Bot running in the same process**

- FastAPI provides HTTP endpoints (`/`, `/health`, `/webhook`)
- Telegram bot connects via webhooks (production) or polling (development)
- Bot is initialized during FastAPI's `startup` event
- Clean shutdown closes both the bot and the HTTP client

### ðŸ“„ `src/bot/handlers.py` â€” Conversation Logic

**Key handlers:**
- `/start` â€” Onboarding flow: checks if user has a home city, asks if not
- `/city` â€” City change flow
- `/settings` â€” Shows user's current configuration
- `handle_message()` â€” The main conversation loop:
  1. If waiting for city: Try static match â†’ fallback to AI detection
  2. If chatting: Detect target city â†’ create AirShieldAgent â†’ get response
  3. Persist chat history to database
  4. Show "Set as home?" button if querying a different city

**`keep_typing()` â€” UX Enhancement**
```python
async def keep_typing(bot, chat_id):
    while True:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(4)
```
- Continuously shows "typing..." indicator while the AI processes
- Telegram's typing indicator expires after 5 seconds, so this refreshes every 4 seconds

### ðŸ“„ `src/bot/proactive_alerts.py` â€” Push Notifications

**"Steel Memory" Logic:**
- **Morning briefing (8-11 AM IST):** Exactly one per user per day. Checks `last_morning_at` date.
- **Hazard alert (AQI > 150):** Maximum once every 4 hours. Checks `last_alert_at` timestamp and 4-hour delta.

---

## 4.8 GitHub Actions & Deployment

### `scrape.yml` â€” Every 30 minutes: Run pipeline + proactive alerts
### `retrain.yml` â€” Every Sunday: Retrain model, commit if improved
### `heartbeat.yml` â€” Every 10 minutes: Ping Render to prevent sleep
### `render.yaml` â€” Render.com deployment blueprint
### `Dockerfile` â€” Python 3.11 slim container with system dependencies
### `docker-compose.yml` â€” PostgreSQL + Web + Worker multi-container setup

---

## 4.9 Test Files

### `tests/test_data_engine.py`
- Tests OpenWeather AQI conversion (1-5 â†’ 0-500)
- Tests outlier clamping (999 â†’ 500)
- Tests "Fattest Dataset" consensus picker
- Tests full end-to-end clean-and-resolve flow

### `tests/test_pipeline.py`
- Tests successful pipeline with mocked scrapers and database
- Tests pipeline survival when one source fails
# AirShield AI â€” Documentation Part 3
# Chapters 5â€“13: Core Logic, Execution Flow, Integration, and More

---

# 5. Core Logic & Algorithms

## 5.1 US EPA AQI Calculation (Linear Interpolation)

The Air Quality Index converts raw PM2.5 concentrations into a standardized 0-500 scale.

**Formula:**
```
AQI = ((I_high - I_low) / (C_high - C_low)) Ã— (C - C_low) + I_low
```

Where:
- `C` = Observed PM2.5 concentration (Î¼g/mÂ³)
- `C_low`, `C_high` = Breakpoint concentration range containing C
- `I_low`, `I_high` = Corresponding AQI range

**Breakpoint Table:**

| PM2.5 Range (Î¼g/mÂ³) | AQI Range | Category |
|:---------------------|:----------|:---------|
| 0.0 â€“ 12.0 | 0 â€“ 50 | Good ðŸŸ¢ |
| 12.1 â€“ 35.4 | 51 â€“ 100 | Moderate ðŸŸ¡ |
| 35.5 â€“ 55.4 | 101 â€“ 150 | Unhealthy for Sensitive Groups ðŸŸ  |
| 55.5 â€“ 150.4 | 151 â€“ 200 | Unhealthy ðŸ”´ |
| 150.5 â€“ 250.4 | 201 â€“ 300 | Very Unhealthy ðŸŸ£ |
| 250.5 â€“ 350.4 | 301 â€“ 400 | Hazardous ðŸŸ¤ |
| 350.5 â€“ 500.4 | 401 â€“ 500 | Hazardous+ âš« |

**Worked Example:**
- PM2.5 = 45.0 Î¼g/mÂ³
- Falls in range (35.5, 55.4) â†’ AQI range (101, 150)
- AQI = ((150-101)/(55.4-35.5)) Ã— (45.0-35.5) + 101
- AQI = (49/19.9) Ã— 9.5 + 101 = 2.462 Ã— 9.5 + 101 = **124**
- Category: Unhealthy for Sensitive Groups ðŸŸ 

## 5.2 XGBoost Regression (PM2.5 Prediction)

**What XGBoost does:** It builds an ensemble of decision trees, where each new tree corrects the errors of the previous trees.

**How it learns:**
1. Tree 1 makes predictions â†’ calculates residuals (errors)
2. Tree 2 is trained to predict the residuals of Tree 1
3. Tree 3 is trained to predict the remaining residuals
4. After 200 trees, the final prediction = sum of all tree outputs

**Feature importance (why these features matter):**
- **PM10**: Strongly correlated with PM2.5 (both are particulate matter)
- **CO, NO2**: Traffic emissions that accompany PM2.5
- **hour**: Rush hours (8 AM, 9 PM) produce more pollution
- **is_winter**: Temperature inversions in winter trap pollutants near ground level
- **city_code**: Different cities have different baseline pollution levels

**Prediction clamping:**
```python
clamped_pred = max(0.0, min(raw_pred, 550.0))
```
Ensures predictions stay within physically possible range.

## 5.3 "Fattest Dataset" Consensus Strategy

When two sources (OpenWeather + AQICN) report for the same city:
```python
best_record = max(
    city_readings,
    key=lambda r: sum(1 for p in POLLUTANT_LIST if r.get(p) is not None)
)
```
Pick the record with more non-null pollutant values. More data = more trustworthy.

## 5.4 "Steel Memory" Alert Logic

**Problem:** Cloud schedulers (GitHub Actions cron) are not perfectly reliable. A "run every 30 minutes" job might run at :00 and :31 and :59 â€” potentially triggering two morning briefings on the same day.

**Solution: Database-level deduplication**
```python
already_briefed = user.last_morning_at.date() == datetime.now(timezone.utc).date()
```
- Before sending a morning briefing, check if today's date matches `last_morning_at`
- If yes â†’ skip. The user already got their briefing today.
- After sending â†’ update `last_morning_at` to current UTC time

**Emergency alert throttle:**
```python
recently_alerted = (last_alert and (now_utc - last_alert) < timedelta(hours=4))
```
- Maximum one emergency alert per 4 hours to prevent notification fatigue.

## 5.5 Exponential Backoff Retry

When API calls fail, the system retries with increasing delays:
- Attempt 1 fails â†’ wait 2 seconds
- Attempt 2 fails â†’ wait 4 seconds
- Attempt 3 fails â†’ wait 8 seconds (capped at 10s max)
- After 3 failed attempts â†’ raise the exception

**Why exponential (not constant)?** If a server is overloaded, constant retries add load. Exponential backoff gives the server breathing room to recover.

---

# 6. Execution Flow

## 6.1 Startup Flow (Running the Bot)

```
User runs: python -m src.bot.bot
    â”‚
    â”œâ”€â”€ 1. config.py loads â†’ reads .env â†’ creates Settings object
    â”‚       â””â”€â”€ ensure_directories() creates data/raw/, data/processed/, data/models/
    â”‚
    â”œâ”€â”€ 2. Uvicorn starts FastAPI app on port 10000
    â”‚
    â”œâ”€â”€ 3. FastAPI startup event fires
    â”‚       â””â”€â”€ start_telegram_bot() as background task
    â”‚           â”œâ”€â”€ Creates HTTPXRequest with configured timeouts
    â”‚           â”œâ”€â”€ Builds Telegram Application with bot token
    â”‚           â”œâ”€â”€ Registers handlers: /start, /city, /settings, messages, buttons
    â”‚           â”œâ”€â”€ If production: Sets webhook URL with Telegram servers
    â”‚           â””â”€â”€ If development: Starts polling for updates
    â”‚
    â””â”€â”€ 4. System ready â€” listening for user messages
```

## 6.2 User Message Flow

```
User sends "How's the air in Pune?" via Telegram
    â”‚
    â”œâ”€â”€ 1. Telegram sends message to bot (via webhook or polling)
    â”‚
    â”œâ”€â”€ 2. handlers.handle_message() receives the Update object
    â”‚       â”œâ”€â”€ Starts keep_typing() background task (shows "typing..." to user)
    â”‚       â”œâ”€â”€ Loads user profile from database (get_or_create_user)
    â”‚       â”‚
    â”‚       â”œâ”€â”€ 3. City Detection:
    â”‚       â”‚       â”œâ”€â”€ validate_city_static("How's the air in Pune?")
    â”‚       â”‚       â”‚       â””â”€â”€ Finds "Pune" via substring matching â†’ returns "Pune"
    â”‚       â”‚       â””â”€â”€ (If static fails: calls AirShieldAgent.identify_city_async â†’ LLM extraction)
    â”‚       â”‚
    â”‚       â”œâ”€â”€ 4. Agent Creation:
    â”‚       â”‚       â””â”€â”€ AirShieldAgent(target_city="Pune", home_city="Mumbai", user_name="Chirag")
    â”‚       â”‚
    â”‚       â”œâ”€â”€ 5. agent.ask("How's the air in Pune?")
    â”‚       â”‚       â”œâ”€â”€ _gather_context():
    â”‚       â”‚       â”‚       â”œâ”€â”€ Calls aqicn_scraper.fetch_air_quality("pune") â†’ live AQI
    â”‚       â”‚       â”‚       â””â”€â”€ Calls predictor.predict_pm25("Pune") Ã— 7 days â†’ forecast
    â”‚       â”‚       â”‚
    â”‚       â”‚       â”œâ”€â”€ Builds system prompt with:
    â”‚       â”‚       â”‚       â”œâ”€â”€ User name, current date/day
    â”‚       â”‚       â”‚       â”œâ”€â”€ Live AQI + PM2.5 values
    â”‚       â”‚       â”‚       â”œâ”€â”€ 7-day forecast with spike warnings
    â”‚       â”‚       â”‚       â””â”€â”€ Tone rules (witty if safe, clinical if hazardous)
    â”‚       â”‚       â”‚
    â”‚       â”‚       â””â”€â”€ Calls NVIDIA NIM API â†’ gets LLM response
    â”‚       â”‚
    â”‚       â”œâ”€â”€ 6. Persist chat history to database
    â”‚       â”œâ”€â”€ 7. Show "Set Pune as Home?" button if different from home city
    â”‚       â””â”€â”€ 8. Cancel keep_typing() task
    â”‚
    â””â”€â”€ User receives personalized air quality advice with forecast
```

## 6.3 ETL Pipeline Flow (Every 30 Minutes)

```
GitHub Actions cron fires at :00 and :30
    â”‚
    â”œâ”€â”€ 1. Spins up Ubuntu Linux VM
    â”œâ”€â”€ 2. Checks out code, installs Python 3.11, installs requirements.txt
    â”‚
    â”œâ”€â”€ 3. Runs: python -m src.data.pipeline
    â”‚       â”œâ”€â”€ _extract_async("OpenWeatherMap", ...) â”€â”€â”
    â”‚       â”œâ”€â”€ _extract_async("AQICN", ...) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤ (concurrent)
    â”‚       â”‚                                             â”‚
    â”‚       â”œâ”€â”€ asyncio.gather() waits for both â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
    â”‚       â”œâ”€â”€ clean_and_resolve() normalizes + picks consensus
    â”‚       â””â”€â”€ save_readings() commits to Supabase PostgreSQL
    â”‚
    â”œâ”€â”€ 4. Runs: python -m src.bot.proactive_alerts
    â”‚       â”œâ”€â”€ Fetches all users with alerts enabled
    â”‚       â”œâ”€â”€ For each user:
    â”‚       â”‚       â”œâ”€â”€ Get latest AQI for their home city
    â”‚       â”‚       â”œâ”€â”€ If 8-11 AM IST and not briefed today â†’ send morning briefing
    â”‚       â”‚       â””â”€â”€ If AQI > 150 and not alerted in 4 hours â†’ send hazard alert
    â”‚       â””â”€â”€ Each notification uses AirShieldAgent for personalized AI text
    â”‚
    â””â”€â”€ 5. VM shuts down (GitHub Actions ephemeral)
```

## 6.4 Self-Evolution Flow (Weekly)

```
GitHub Actions cron fires every Sunday at midnight UTC
    â”‚
    â”œâ”€â”€ 1. Runs: python src/ml/train_continuous.py
    â”‚       â”œâ”€â”€ check_data_readiness() â†’ need â‰¥ 50 readings
    â”‚       â”œâ”€â”€ Downloads ALL readings from Supabase PostgreSQL
    â”‚       â”œâ”€â”€ Feature engineering (hour, month, day_of_week, is_winter, city_code)
    â”‚       â”œâ”€â”€ Train/test split (80/20)
    â”‚       â”œâ”€â”€ Train new XGBoost model with MLflow tracking
    â”‚       â”œâ”€â”€ Evaluate RÂ² score
    â”‚       â”‚
    â”‚       â”œâ”€â”€ If RÂ² â‰¥ 0.70:
    â”‚       â”‚       â”œâ”€â”€ Save new model as xgboost_pm25.joblib (replaces old one)
    â”‚       â”‚       â””â”€â”€ Log to MLflow as "Champion-Model"
    â”‚       â”‚
    â”‚       â””â”€â”€ If RÂ² < 0.70:
    â”‚               â””â”€â”€ Keep old model. Log warning.
    â”‚
    â”œâ”€â”€ 2. Check if model file changed (git diff)
    â”œâ”€â”€ 3. If changed: git add, commit, push new model to GitHub
    â””â”€â”€ 4. Next deployment picks up the improved model automatically
```

---

# 7. Integration Between Modules

## 7.1 How Components Connect

```
config.py â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€> EVERY module (settings singleton)
cities.py â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€> scrapers, agent, predictor, handlers, historical_loader
logger.py â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€> EVERY module (logging)
time_utils.py â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€> queries, advisor, predictor
retry.py â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€> openweather_scraper, aqicn_scraper
http_client.py â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€> openweather_scraper, aqicn_scraper, advisor

pipeline.py â”€â”€â”€> scrapers + cleaner + queries (ETL flow)
handlers.py â”€â”€â”€> queries + advisor + cities (chat flow)
proactive_alerts.py â”€â”€â”€> queries + advisor (push flow)
train_continuous.py â”€â”€â”€> predictor (CITY_CODES) + config (paths)
```

## 7.2 Data Exchange Formats

**Scraper output format (dict):**
```python
{
    "city": "Delhi",
    "aqi": 125,
    "pm2_5": 45.2,
    "pm10": 88.0,
    "co": 1200.0,
    "no": None,
    "no2": 35.0,
    "o3": 40.0,
    "so2": 12.5,
    "nh3": None,
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timestamp": "2026-04-09T12:00:00+00:00",
    "source": "aqicn"
}
```

**Prediction output format (dict):**
```python
{
    "city": "Delhi",
    "predicted_pm25": 67.43,
    "hour": 12,
    "month": 4,
    "is_winter": False
}
```

---

# 8. Error Handling & Edge Cases

| Scenario | How System Handles It |
|:---------|:---------------------|
| API timeout | `@sentinel_retry` retries 3Ã— with exponential backoff |
| API rate limit (429) | Retry decorator waits and tries again |
| API returns invalid data | `clean_reading()` rejects records missing mandatory fields |
| AQI value = 999 (sensor error) | Clamped to 500 maximum |
| Negative pollutant values | Set to None by cleaner |
| One scraper source fails | Pipeline continues with the other source's data |
| Database write fails for one record | Per-record try/except; other records still save |
| ML model file missing | `predictor.py` returns `predicted_pm25: 0.0` with error flag |
| LLM API fails | Agent tries 3 NVIDIA NIM models in sequence |
| All LLM models fail | Returns friendly fallback message |
| User types non-city text during onboarding | Static match fails â†’ AI extraction â†’ if still fails, asks again (max 3 retries) |
| Duplicate morning briefing risk | "Steel Memory" checks `last_morning_at` date before sending |
| Alert spam risk | 4-hour throttle on emergency alerts |
| Unknown city requested | Agent logs warning, returns error context |
| PostgreSQL timezone-aware datetime | `to_naive_utc()` strips timezone info |
| PgBouncer connection pooling conflicts | "Giga-Sledgehammer" disables prepared statement caching |

---

# 9. Performance Considerations

## 9.1 Optimizations Implemented

1. **Singleton HTTP client** â€” One connection pool for all requests (prevents socket exhaustion)
2. **Singleton model loader** â€” ML model loaded once into RAM, reused for all predictions
3. **Concurrent scraping** â€” `asyncio.gather()` fetches all cities simultaneously
4. **Semaphore throttling** â€” `asyncio.Semaphore(10)` prevents overwhelming APIs
5. **Batch database inserts** â€” Historical loader uses 5000-row batches
6. **Indexed database columns** â€” `city` column indexed for O(log n) lookups
7. **Connection pooling** â€” SQLAlchemy engine maintains pool with `pool_pre_ping=True`
8. **Log rotation** â€” 7-day retention prevents disk space exhaustion

## 9.2 Memory Usage

- XGBoost model in memory: ~5 MB
- HTTP client connection pool: ~2 MB
- SQLAlchemy engine pool: ~10 MB
- **Total application memory:** ~50-100 MB (fits in Render free tier)

## 9.3 Bottlenecks and Solutions

| Bottleneck | Impact | Solution |
|:-----------|:-------|:---------|
| LLM API latency (3-8s) | User waits for response | `keep_typing()` UX indicator |
| Database over network | ~100ms per query | Async sessions (non-blocking) |
| 7-day forecast (7 predictions) | ~50ms total | Singleton model (no disk I/O) |
| Large training dataset | ~300K rows | Chunked reading with `pd.read_sql(chunksize=50000)` |

---

# 10. Installation & Setup Guide

## Step 1: Clone the Repository
```bash
git clone https://github.com/Chirag-Jogi/AirShield-AI.git
cd AirShield-AI
```

## Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Configure API Keys
Create a `.env` file in the project root:
```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
NVIDIA_API_KEY=nvapi-your_nvidia_nim_key
OPENWEATHER_API_KEY=your_openweather_key
AQICN_API_KEY=your_aqicn_key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
WEBHOOK_URL=https://your-app.onrender.com/webhook
APP_ENV=development
```

## Step 5: Initialize Database
```bash
python -c "import asyncio; from src.database.connection import init_db; asyncio.run(init_db())"
```

## Step 6: Run the Bot (Development Mode)
```bash
python -m src.bot.bot
```

## Step 7: Deploy to Render (Production)
1. Push code to GitHub
2. Connect repository to render.com
3. Add environment variables in Render dashboard
4. Deploy as Blueprint using `render.yaml`

---

# 11. Testing & Validation

## Running Tests
```bash
pytest tests/ -v
```

## Test Cases Included

**test_data_engine.py:**
- `test_clean_reading_normalization` â€” Verifies OpenWeather AQI 3 â†’ EPA 125
- `test_outlier_clamping` â€” Verifies AQI 999 â†’ clamped to 500
- `test_consensus_fattest_dataset` â€” Verifies source with more pollutants is picked
- `test_full_clean_and_resolve_flow` â€” End-to-end 3 readings â†’ 2 resolved

**test_pipeline.py:**
- `test_run_pipeline_async_success` â€” Full pipeline with mocked scrapers
- `test_pipeline_survival_on_source_failure` â€” One source fails, pipeline still saves

---

# 12. Future Improvements

1. **Multi-country support** â€” Extend beyond India to global cities
2. **Indoor air quality** â€” Integrate with smart home sensors (e.g., Xiaomi)
3. **Satellite integration** â€” NASA/ESA satellite imagery for rural areas without sensors
4. **Email/SMS alerts** â€” Additional notification channels beyond Telegram
5. **User health profiles** â€” Customize thresholds for asthma patients vs. healthy adults
6. **Time-series models** â€” Add LSTM/Transformer models for temporal pattern learning
7. **Real-time dashboard** â€” Web UI with live charts and maps
8. **Multi-language support** â€” Hindi, Marathi, Tamil bot responses
9. **Pollen/UV monitoring** â€” Extend beyond air quality to broader health metrics
10. **Mobile app** â€” Native iOS/Android companion app

---

# 13. Glossary

| Term | Simple Explanation |
|:-----|:-------------------|
| **AQI** | Air Quality Index â€” a number from 0 to 500 where higher = more dangerous air |
| **PM2.5** | Tiny particles in the air (2.5 micrometers) that can enter your lungs |
| **ETL** | Extract-Transform-Load â€” the process of collecting, cleaning, and saving data |
| **XGBoost** | A machine learning algorithm that builds many decision trees to make predictions |
| **RÂ² Score** | A measure of prediction accuracy (1.0 = perfect, 0.0 = random guessing) |
| **MAE** | Mean Absolute Error â€” average difference between predicted and actual values |
| **RMSE** | Root Mean Square Error â€” like MAE but penalizes big errors more |
| **ORM** | Object-Relational Mapping â€” lets you use Python objects instead of writing SQL |
| **SQLAlchemy** | A Python library that translates Python classes into database tables |
| **Pydantic** | A Python library that validates data types and loads settings from files |
| **FastAPI** | A modern Python web framework for building APIs |
| **Webhook** | A URL that receives HTTP requests â€” Telegram pushes messages to our webhook |
| **Polling** | Repeatedly asking Telegram "Any new messages?" â€” used in development |
| **Singleton** | A design pattern where only one instance of an object exists in memory |
| **Async/Await** | Python's way of running multiple operations concurrently without threads |
| **Semaphore** | A counter that limits how many tasks can run at the same time |
| **Exponential Backoff** | Waiting progressively longer between retries (2s, 4s, 8s...) |
| **NVIDIA NIM** | NVIDIA's serverless AI inference service for running LLMs in the cloud |
| **LLM** | Large Language Model â€” AI that understands and generates human text |
| **RAG** | Retrieval-Augmented Generation â€” giving an AI real data before asking it to respond |
| **Cron Job** | A scheduled task that runs automatically at specified times |
| **GitHub Actions** | GitHub's free CI/CD service for running automated tasks |
| **Docker** | A tool that packages applications into standardized containers |
| **Render** | A cloud platform for hosting web services |
| **Supabase** | A managed PostgreSQL database service (like Firebase but SQL) |
| **MLflow** | A tool for tracking ML experiments, their parameters, and results |
| **Joblib** | A library for saving/loading Python objects (used for ML models) |
| **HTTPX** | A modern Python HTTP client library (async-capable replacement for requests) |
| **Tenacity** | A Python library for adding retry logic to functions |
| **Loguru** | A Python logging library with colorful output and automatic file rotation |
| **PgBouncer** | A connection pooler for PostgreSQL that manages database connections efficiently |

---

# 14. Version 2.1 — Production Resilience Upgrade (April 2026)

## 14.1 Dual-Source AQI Verification

**Problem:** The system previously relied solely on AQICN for live AQI data. AQICN returns pre-calculated sub-indices (not raw concentrations), and these values sometimes differed significantly from other sources like aqi.in. The PM2.5 value was also incorrectly labeled as "μg/m³" when it was actually a sub-index value.

**Solution:** The agent now fetches from **both OpenWeatherMap and AQICN** simultaneously using `asyncio.gather()`:
- **OpenWeather** provides raw PM2.5 in μg/m³ → we calculate AQI ourselves using the US EPA formula
- **AQICN** provides a pre-calculated AQI for cross-verification
- If sources disagree by more than 30%, the system uses the **higher (safer) value**
- PM2.5 is now correctly displayed with the proper μg/m³ unit

```python
results = await asyncio.gather(aqicn_task, ow_task, return_exceptions=True)
```

## 14.2 Intelligent AQI Cache

**Problem:** Every user message triggered 2 API calls (AQICN + OpenWeather). With multiple users asking about the same city, this wasted rate limits and added unnecessary latency.

**Solution:** In-memory cache with 5-minute TTL per city:
```python
_aqi_cache: Dict[str, Dict] = {}
AQI_CACHE_TTL = 300  # 5 minutes
```
- First request for a city: fetches from APIs (~3s) and caches the result
- Subsequent requests within 5 minutes: served instantly from cache
- **Tested result:** 1st call = 16.5s, 2nd call (cached) = 4.7s — **3.5x faster**

## 14.3 Smart LLM Fallback Chain

**Problem:** The system only used NVIDIA NIM models. When rate-limited (free tier: ~5-10 req/min), ALL requests failed with a generic error message.

**Solution:** Two-tier fallback architecture:
```
NVIDIA NIM (Tier 1: fastest, best quality)
├── meta/llama-3.1-70b-instruct
├── meta/llama-3.1-405b-instruct
└── ALL FAILED? ↓
OpenRouter Free Models (Tier 2: 10+ options)
├── Models shuffled randomly each request (load balancing)
├── Round-robin key rotation across multiple API keys
└── Try max 4 models → Return first success
```
- NVIDIA models are tried first (sub-5-second inference)
- If all NVIDIA models fail, OpenRouter free models are tried as backup
- 10+ free models are shuffled randomly to distribute load
- Applied to both `ask()` and `identify_city_async()` functions

## 14.4 OpenRouter Key Rotation

**Problem:** A single API key has a rate limit of ~10 requests/minute. Under load, this limit is quickly exhausted.

**Solution:** Round-robin rotation through all available keys:
```python
def _get_next_openrouter_key() -> str:
    keys = settings.get_openrouter_keys()  # Comma-separated from .env
    key = keys[_or_key_index % len(keys)]
    return key
```
- 1 key = 10 req/min, 3 keys = 30 req/min capacity
- Keys are configured via `OPENROUTER_API_KEYS` in `.env` (comma-separated)

## 14.5 Real-Time Clock Fix

**Problem:** The bot displayed a fixed/stale time in every response (e.g., always showing "10:15" regardless of when the user asked). The LLM was picking up an old timestamp from cached context data instead of the current time.

**Root causes identified:**
1. The `_gather_context()` method cached a `timestamp` field that the LLM used instead of the fresh time
2. The time instruction in the system prompt was too weak — the LLM treated it as optional

**Solution (3 changes):**
1. Removed the stale `timestamp` field from context data
2. Context is now always re-fetched on every `ask()` call (with cache for AQI data, but fresh time computation)
3. Added forceful time instruction in the system prompt:
```python
f"⏰ THE CURRENT TIME IS EXACTLY: **{current_time_str} IST**\n"
f"YOU MUST USE THIS EXACT TIME ({current_time_str}) IN YOUR RESPONSE HEADER.\n"
```

## 14.6 Capacity Assessment After Upgrades

| Users per minute | Status | Why |
|:---|:---|:---|
| 1-5 | ✅ Smooth | NVIDIA handles all requests |
| 5-15 | ✅ Reliable | Cache + NVIDIA with occasional OpenRouter fallback |
| 15-30 | ⚠️ Some delays | NVIDIA rate-limited → OpenRouter catches overflow |
| 30-50 | ⚠️ Manageable | Full OpenRouter with key rotation + cache keeps it alive |

---

**END OF DOCUMENTATION**

> This document covers the COMPLETE AirShield AI project from zero to full understanding.
> Every file, every function, every algorithm, and every design decision has been explained.
