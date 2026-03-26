<div align="center">
  <img src="https://img.icons8.com/parakeet-line/128/000000/air-quality.png" alt="AirShield Logo" width="100"/>
  <h1>AirShield AI 🌍🌬️</h1>
  <p><strong>An Industry-Grade Air Pollution Prediction & AI Health Advisor Platform</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?logo=postgresql&logoColor=white)](https://supabase.com)
  [![XGBoost](https://img.shields.io/badge/Machine%20Learning-XGBoost-orange?logo=scikit-learn)](https://xgboost.readthedocs.io/)
  [![Docker](https://img.shields.io/badge/Architecture-Docker-2496ED?logo=docker&logoColor=white)](https://docker.com)
</div>

<br>

## 📖 Overview
**AirShield AI** is an advanced, full-stack data engineering and machine learning platform designed to tackle one of the world's most pressing health crises: Air Pollution. 

Rather than simply displaying current Air Quality Index (AQI) values, AirShield AI implements an automated **Extract, Transform, Load (ETL) pipeline** that scrapes live meteorological data across 20 major Indian cities, stores it in a cloud PostgreSQL database, and utilizes a highly-trained **XGBoost Machine Learning model** to forecast PM2.5 pollution levels up to 7 days into the future. 

Furthermore, the platform integrates an **autonomous LLM Agent** (powered by NVIDIA Nemotron 30B / Meta Llama 3 via OpenRouter) that dynamically analyzes these mathematical predictions to provide contextual, hyper-personalized respiratory health and scheduling advice to vulnerable individuals.

---

## ⚡ Key Features

* **📡 Automated ETL Pipeline:** A Python-based background scheduler (`APScheduler`) routinely extracts live pollutant metrics (PM2.5, PM10, NO2, SO2, O3) and meteorological data from the OpenWeatherMap API, processing and writing it to a persistent PostgreSQL database.
* **🔮 Predictive ML Engine:** A pre-trained XGBoost regression model (trained on historical datasets) evaluates complex weather patterns, temperature inversions, wind speeds, and temporal data (month, day-of-week) to predict severe pollution events before they happen.
* **🤖 Multi-Model AI Health Advisor:** An integrated generative AI agent designed to consume numerical ML forecasts. It acts as a respiratory health consultant. If the primary LLM faces rate limits (HTTP 429), the Agent's resilient failover architecture seamlessly reroutes the request through a designated cascade of ultra-fast fallback models (e.g., Gemma 27B, Mistral 24B).
* **🗺️ Interactive Geospatial Dashboard:** Built with Streamlit and Folium, the dashboard provides a dynamic choropleth map of India, allowing users to visually track massive pollution fronts moving across the subcontinent in real-time.
* **📊 Time-Series Analytics:** Interactive Plotly graphs map 24-hour PM2.5 forecasts and allow for direct cross-city pollutant comparisons.
* **🐳 Docker Microservices:** The entire architecture is containerized. A `docker-compose` network isolates the Streamlit web GUI from the background scraping worker, ensuring production-grade scalability.

---

## 🏗️ System Architecture

mermaid
graph TD;
    A[OpenWeatherMap API] -->|"Live Data (JSON)"| B(Data Scraper & Cleaner);
    B -->|"Cleaned DataFrame"| C[(Supabase PostgreSQL Database)];
    C -->|"Historical & Live Data"| D[XGBoost ML Predictor];
    
    D -->|"7-Day PM2.5 Forecast"| E[LLM Context Generator];
    E -->|"Structured Prompt"| F[OpenRouter API];
    F -->|"Nemotron / Llama-3"| G{Agent Failover Router};
    G -->|"AI Health Advice"| H[Streamlit Web Dashboard];
    
    C -->|"Live Metrics"| H;
    
    subgraph "Docker Container Network"
    H
    B
    end



### Tech Stack
| Tier | Technologies Used |
| :--- | :--- |
| **Frontend UI** | Streamlit, Plotly (Data Viz), Folium (Maps) |
| **Backend / DB** | Python, SQLAlchemy (ORM), PostgreSQL (Supabase Cloud) |
| **Machine Learning** | Scikit-Learn, XGBoost, Pandas, Numpy, Joblib |
| **Generative AI** | OpenRouter REST API, NVIDIA Nemotron 30B, Meta Llama-3 |
| **Data Engineering** | APScheduler, Background CLI Workers |
| **DevOps** | Docker, Docker-Compose, Streamlit Community Cloud |

---

## 🚀 Getting Started

Follow these steps to deploy the AirShield AI platform on your local machine or server.

### 1. Prerequisites
You must have Python 3.11+ (or Docker) installed on your system. You will also need three free API keys:
1. **[OpenWeatherMap API Key](https://openweathermap.org/api):** For live meteorological data.
2. **[OpenRouter API Key](https://openrouter.ai/):** For free access to advanced LLMs.
3. **[Supabase Project URL](https://supabase.com/):** For the cloud PostgreSQL connection pooling string.

### 2. Installation (Standard Python)

Clone the repository and install the dependencies:
```bash
git clone https://github.com/yourusername/airshield-ai.git
cd airshield-ai

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root of the project and inject your credentials:
```env
OPENWEATHER_API_KEY=your_openweathermap_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
DATABASE_URL=postgresql://postgres.xxx:password@aws-0.pooler.supabase.com:6543/postgres
```

### 4. Database Initialization & Data Seeding
Before launching the UI, you must compile the SQL schema and scrape the initial batch of live data into your cloud database:
```bash
# 1. Build the tables in Supabase
python -c "from src.database.connection import init_db; init_db()"

# 2. Trigger the automated ETL pipeline (runs a live scrape)
python -m src.data.pipeline
```

### 5. Launching the Platform

**Option A: Running Locally (Streamlit)**
```bash
streamlit run dashboard/app.py
```
*The web interface will instantly become available at `http://localhost:8501`.*

**Option B: Running via Docker (Production Microservices)**
AirShield AI comes pre-configured with a powerful dual-container architecture.
```bash
docker compose up --build
```
*This command will spin up two isolated containers:*
1. **`airshield_web`**: Hosts the Streamlit frontend UI.
2. **`airshield_worker`**: Runs the Python `APScheduler` infinitely in the background, updating the Supabase database automatically every hour.

---

## 🔬 Machine Learning Performance (XGBoost)
The predictive model was trained on historical Indian air quality datasets targeting the highly volatile PM2.5 metric. 
* **Model Type:** Extreme Gradient Boosting Regressor (`XGBRegressor`)
* **Core Features:** Temperature, Humidity, AQI, Day of Week, Month
* **R² Score:** 0.77+ (Demonstrates strong correlation between meteorological inputs and severe pollution spikes).

---

## 👨‍💻 Developed By
**Chirag**  
*Data Scientist & AI Engineer*  
Passionate about building highly-scalable, socially-impactful AI applications leveraging modern data workflows.

---
*If you find this repository useful, feel free to give it a ⭐!*
