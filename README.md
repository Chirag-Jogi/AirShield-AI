# AirShield AI 🌍🤖

**An Industry-Grade Air Pollution Prediction & Intelligence Platform**

AirShield AI is a full-stack, real-time data engineering and machine learning platform that doesn't just track air pollution—it predicts it. By combining live API scrapers, an automated ETL pipeline, custom XGBoost forecasting models, and OpenRouter-powered AI Agents, AirShield AI delivers unparalleled, mathematically precise respiratory health intelligence for major cities across India.

---

## 🚀 Features

* **Real-Time Data Pipeline:** Automated Python scrapers pull live environmental data (AQI, PM2.5, PM10, Gases) from OpenWeatherMap APIs.
* **XGBoost Machine Learning Forecast:** Pre-trained ML models predict PM2.5 levels up to 7 days into the future with high accuracy, parsing meteorological cycles.
* **Agentic AI Health Advisor:** An advanced LLM agent (via OpenRouter) powered by real-time numerical context and future ML predictions. It understands relative probability and outputs calculated health risk analysis.
* **Cloud Database Architecture:** Fully migrated to a Supabase PostgreSQL backend structured for cloud environments.
* **Interactive Streamlit Dashboard:** Professional-grade visualizations via Plotly and Folium, offering live dynamic mapping, historical comparison, and real-time inference.

---

## 🏗️ System Architecture

* **Frontend:** Streamlit, Plotly, Folium
* **Backend Database:** PostgreSQL (Supabase), SQLAlchemy (ORM)
* **API Providers:** OpenWeatherMap, OpenRouter (LLM routing)
* **Machine Learning:** Scikit-learn, XGBoost
* **Automation:** APScheduler / Background cloud cron triggers
* **Deployment:** Docker, Streamlit Community Cloud

---

## 💻 Running the Project Locally

### 1. Requirements
* Python 3.11+
* Supabase PostgreSQL URL
* API Keys for OpenWeather and OpenRouter

### 2. Setup
Clone the repository and install dependencies:
```bash
git clone https://github.com/yourusername/airshield-ai.git
cd airshield-ai
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
OPENWEATHER_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres.xxx:password@aws-0.pooler.supabase.com:6543/postgres
```

### 4. Running the Complete Stack

**Option A: Standard Python**
1. Initialize Database schema:
```bash
python -c "from src.database.connection import init_db; init_db()"
```
2. Start the App:
```bash
streamlit run dashboard/app.py
```

**Option B: Docker Microservices**
AirShield AI is fully containerized into a multi-container stack.
```bash
docker compose up --build
```
*(This automatically runs the pipeline worker in the background while bringing the web UI online).*

---

## 🧠 The AI Agent

AirShield AI operates a fully autonomous LLM agent equipped with the `FREE_MODELS` routing system. If a specific ML parameter set causes a model rate-limit (HTTP 429), the Agent silently sleeps and reroutes the user prompt through an extensive fallback list of ultra-fast models (like Nemotron 30B or Llama-3 3B), ensuring near-100% uptime for health queries.
