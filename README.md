<div align="center">
  <img src="https://img.icons8.com/parakeet-line/128/000000/air-quality.png" alt="AirShield Logo" width="100"/>
  <h1>AirShield AI 🌍🛡️</h1>
  <p><strong>The "Elite" 24/7 Proactive AI Guardian for Respiratory Health</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
  [![Telegram](https://img.shields.io/badge/Interface-Telegram_Bot-26A5E4?logo=telegram&logoColor=white)](https://t.me/AirShield_Bot)
  [![PostgreSQL](https://img.shields.io/badge/DB-Supabase_PostgreSQL-336791?logo=postgresql&logoColor=white)](https://supabase.com)
  [![Hosting](https://img.shields.io/badge/Cloud-Render-46E3B7?logo=render&logoColor=white)](https://render.com)
  [![Automation](https://img.shields.io/badge/Automation-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
  
  <br/>
  
  ### 🛡️ [Interact with the Guardian Bot: @AirShield_Bot](https://t.me/AirShield_Bot)
</div>

---

## 📖 Overview
**AirShield AI** is a production-grade, cloud-native MLOps platform that evolves air quality monitoring from passive data display to **proactive health protection**. 

Built for modern urban environments, AirShield acts as a "Concierge for your Lungs." It automatically scrapes live pollutant data across 20+ major cities, predicts future spikes using an **XGBoost Machine Learning model**, and provides personalized health advice through a witty, caring **Telegram AI Buddy**.

Unlike standard trackers, AirShield implements **"Steel Memory" logic**—a stateful alerting system that ensures you get exactly one morning briefing and real-time emergency warnings only when you truly need them, regardless of cloud scheduling fluctuations.

---

## ⚡ Key Features

* **🤖 24/7 AI Guardian (Telegram):** An interactive LLM-powered bot (NVIDIA Nemotron 30B / Llama 3) that adopts a casual, "Swiggy-style" personal buddy persona. No jargon, just witty and actionable health advice.
* **🧠 Steel Memory Logic:** A custom state-tracking engine built on PostgreSQL that prevents notification spam and ensures resilient daily deliveries despite GitHub Action scheduling delays.
* **📡 Autonomous ETL Pipeline:** A serverless data harvester that wakes up every 30 minutes via **GitHub Actions** to extract, transform, and load meteorological metrics into the cloud.
* **🔮 Predictive ML Engine:** An XGBoost regressor that evaluates 24-hour weather patterns and wind speeds to forecast PM2.5 trends with an **R² score of 0.77+**.
* **🏙️ Multi-City Persistence:** Tracks individual user preferences, home cities, and alert history for hyper-personalized health monitoring.

---

## 🏗️ System Architecture

```mermaid
graph TD;

    subgraph "Cloud Automation (GitHub)"
        A[GitHub Actions Scraper] -->|"30-min Cron"| B[ETL Pipeline];
    end

    subgraph "External APIs"
        C[OpenWeatherMap] --> B;
        D[AQICN API] --> B;
    end

    subgraph "Database Tier (Supabase)"
        B -->|"Sync"| E[(Supabase PostgreSQL)];
    end

    subgraph "Intelligence Tier"
        E -->|"Features"| F[XGBoost Forecaster];
        F -->|"Predictions"| G[AI Agent Context];
        H[OpenRouter LLM] <--> G;
    end

    subgraph "Communication Tier (Render)"
        G --> I[AirShield Bot Service];
        I <--> J[Telegram User];
    end
 ```   

### Tech Stack
| Tier | Technologies |
| :--- | :--- |
| **Interface** | Python-Telegram-Bot, HTTPX (Sentinel Client) |
| **Logic/State** | Python 3.11, SQLAlchemy, Pydantic, Tenacity |
| **Database** | PostgreSQL (Supabase Cloud) |
| **Predictive AI** | XGBoost, Scikit-Learn, Pandas, MLflow |
| **Generative AI** | NVIDIA Nemotron 30B, Meta Llama-3 (via OpenRouter) |
| **Cloud/DevOps** | Render (24/7 Bot), GitHub Actions (Scraper), Docker |

---

## 🚀 Deployment & Setup

### 1. Prerequisites
You need four free API keys to go live:
1. **[Bot Token](https://t.me/Botfather):** From Telegram BotFather.
2. **[OpenWeather API](https://openweathermap.org/api):** For meteorological data.
3. **[OpenRouter API](https://openrouter.ai/):** For model access.
4. **[Supabase DB URL](https://supabase.com/):** For cloud PostgreSQL.

### 2. Standard Installation
```bash
git clone https://github.com/Chirag-Jogi/AirShield-AI.git
pip install -r requirements.txt
python -m src.bot.bot
```

### 3. Environment Secrets (.env)
```env
TELEGRAM_BOT_TOKEN=your_token
OPENROUTER_API_KEY=your_key
DATABASE_URL=your_supabase_url
OPENWEATHER_API_KEY=your_key
AQICN_API_KEY=your_key
```

### 4. 24/7 Cloud Hosting (Render)
This repository includes a `render.yaml` blueprint. Simply connect your GitHub repo to [Render.com](https://render.com) and deploy as a **Blueprint Instance**. All configurations and health checks are handled automatically.

---

## 👨‍💻 Developed By
**Chirag**  
*AI Engineer & Data Engineer*  
*Specializing in High-Performance Agentic Pipelines and MLOps.*

---
*If you find this project impactful, feel free to give it a ⭐!*
