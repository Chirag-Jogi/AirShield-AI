# 🎓 AirShield AI: The Ultimate Technical Master Class

This document is a **comprehensive, line-by-line technical autopsy** of the entire AirShield AI project. It is designed to be read sequentially, like a textbook, providing a deep deconstruction of every component, from configuration to AI-driven health advice.

---

## 🏛️ Chapter 1: Project Overview & Folder Structure

### 📖 Project Objective
AirShield AI is an enterprise-grade Environmental Intelligence platform. It solves the problem of "invisible killers" (air pollutants) by combining real-time data ingestion with predictive machine learning and generative AI.

1.  **Ingest:** Scraping live PM2.5 and meteorological data for 20 Indian cities.
2.  **Predict:** Using XGBoost to forecast pollution levels for the next 7 days.
3.  **Advise:** Using an LLM Agent to provide personalized health recommendations based on those predictions.

### 📂 Folder Structure Deconstruction

| Folder / File | Purpose |
| :--- | :--- |
| `dashboard/` | **The Frontend.** Contains the Streamlit web application and its multi-page setup. |
| `data/` | **The Storage.** Holds the SQLite database, raw CSVs, and pre-trained ML model artifacts (.joblib). |
| `logs/` | **The Diary.** Stores automated execution logs for debugging the hourly scrapers. |
| `notebooks/` | **The Lab.** Contains Jupyter notebooks used for initial data analysis and model training experiments. |
| `scheduler/` | **The Heartbeat.** Contains the background automation logic that triggers the ETL pipeline. |
| `src/` | **The Engine Room.** The core Python package containing all modular logic. |
| `src/agent/` | **The Brain.** Logic for the LLM-powered Health Advisor. |
| `src/data/` | **The Ingestion.** Scrapers, cleaners, and the main ETL pipeline logic. |
| `src/database/` | **The Memory.** Database connection pooling, SQL models (ORM), and queries. |
| `src/ml/` | **The Oracle.** Feature engineering and prediction logic for the XGBoost model. |
| `src/utils/` | **The Tools.** General-purpose helpers for logging, time-synchronization, and API retries. |
| `.github/workflows/`| **The Ghost.** Automates the data scraping using GitHub Actions (CI/CD). |

---

## ⚙️ Chapter 2: Config & Environment (The Foundation)

Before a single line of logic runs, the system must know *how* to run. This chapter deconstructs the environment setup.

### 📄 File: [config.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/config.py)
**Purpose:** The central "Source of Truth" for all project variables. It ensures that if we change a setting once here, it updates across the entire system.

#### Code Breakdown:
```python
12: BASE_DIR = Path(__file__).resolve().parent
```
*   **What it does:** Finds the absolute path to the folder where `config.py` lives.
*   **Why it exists:** We need reliable paths for the `data/` and `logs/` folders regardless of where the app is deployed (Windows, Linux, or Docker).
*   **What breaks if removed:** The app won't be able to find the database or ML models.

```python
15: class Settings(BaseSettings):
```
*   **What it does:** Uses Pydantic to create a structured configuration object.
*   **Why it exists:** Pydantic automatically converts strings from `.env` into Python types (like `int` or `float`) and validates them.
*   **What breaks if removed:** We'd have to manually parse strings, leading to "TypeErrors" later.

```python
24: OPENWEATHER_API_KEY: str = ""
```
*   **What it does:** Defines a variable for the weather API.
*   **Why it exists:** It acts as a "placeholder" that gets filled by the `.env` file.
*   **What breaks if removed:** The scraper won't know where to get the API key.

```python
36: DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'airshield.db'}"
```
*   **What it does:** Sets the default database to a local file.
*   **Why it exists:** Ensures the app works "out of the box" even if the user hasn't set up a cloud Supabase database yet.

```python
46: model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"))
```
*   **What it does:** Tells the code: "Go look for a file named `.env` and read its contents into this class."
*   **Why it exists:** Keeps secrets (API keys) out of the code and safe in a hidden file.

```python
60: settings = Settings()
61: settings.ensure_directories()
```
*   **What it does:** Automatically creates the `data/raw/` and `data/models/` folders when the app starts.
*   **Why it exists:** Prevents "File Not Found" errors during the first run.

---

### 📄 File: [.env.example](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/.env.example)
**Purpose:** A template for other developers to know which API keys they need to provide.

#### Code Breakdown:
```text
2: OPENWEATHER_API_KEY=your_key_here
```
*   **What it does:** Shows that an OpenWeather key is required.
*   **Why it exists:** Developers never check in their *real* `.env` file to GitHub (security risk). This file tells them the "shape" of the secrets needed.

---

### 📄 File: [requirements.txt](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/requirements.txt)
**Purpose:** The "Shopping List" of all external libraries needed to run the project.

#### Important Dependencies:
*   **`pydantic-settings`**: Handles the configuration deconstructed above.
*   **`sqlalchemy`**: The "Translator" that lets Python talk to SQL databases.
*   **`xgboost`**: The Machine Learning engine.
*   **`streamlit`**: The web dashboard framework.
*   **`psycopg2-binary`**: The driver for connecting to professional PostgreSQL databases (Supabase).

---

### 📄 File: [Dockerfile](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/Dockerfile)
**Purpose:** Standardizes the environment. It ensures the app runs EXACTLY the same on Chirag's computer as it does on a cloud server.

#### Code Breakdown:
```dockerfile
2: FROM python:3.11-slim
```
*   **What it does:** Downloads a tiny, optimized Linux operating system with Python 3.11 pre-installed.
*   **Why it exists:** Avoids "It works on my machine" bugs.

```dockerfile
12: RUN apt-get update && apt-get install -y build-essential libgomp1
```
*   **What it does:** Installs low-level tools needed for the XGBoost ML library to perform fast math.
*   **Why it exists:** Without `libgomp1`, the ML model will crash in a Linux environment.

```dockerfile
24: COPY . .
```
*   **What it does:** Copies all your project files into the virtual Linux container.

---

### 📄 File: [docker-compose.yml](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/docker-compose.yml)
**Purpose:** Orchestrates multiple "Workers" to run at once.

#### Service Breakdown:
1.  **`db`**: Spins up a local PostgreSQL database for testing.
2.  **`web`**: Runs the Streamlit Frontend on port 8501.
3.  **`worker`**: Runs the Background Scraper. It uses `python -c "from scheduler.jobs import start_scheduler; start_scheduler()"` to keep the data flowing.

---

---

## 🕒 Chapter 3: Utilities (The Helper Tools)

Before the system can scrape data or predict the future, it needs a set of "Swiss Army Knife" tools to handle common problems like network failures, logging, and timezones.

### 📄 File: [src/utils/retry.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/utils/retry.py)
**Purpose:** Handles unreliable network connections. If an API (like OpenWeather) fails momentarily, this script "retries" the call automatically instead of letting the whole app crash.

#### Code Breakdown:
```python
20: def retry_on_failure(..., max_retries: int | None = None, base_delay: float | None = None, ...):
```
*   **What it does:** Defines a "Decorator"—a special function that wraps around *other* functions to give them "superpowers."
*   **Why it exists:** We don't want to write retry logic inside every single API call. This allows us to just add `@retry_on_failure` above any function.

```python
50: for attempt in range(1, _max_retries + 1):
```
*   **What it does:** Starts a loop. It will try to run the function up to 3 times (the default in `config.py`).
*   **Why it exists:** Temporary internet glitches usually resolve within a few seconds.

```python
56: delay = _base_delay * (2 ** (attempt - 1))
```
*   **What it does:** This is **Exponential Backoff**. 
    *   Attempt 1 fail → Wait 2 seconds.
    *   Attempt 2 fail → Wait 4 seconds.
*   **Why it exists:** If a server is overloaded, hitting it again immediately makes it worse. This "backs off" to give the server breathing room.

```python
62: time.sleep(delay)
```
*   **What it does:** Makes the program "pause" for the calculated delay.
*   **What breaks if removed:** The retries would happen instantly, likely failing again for the same reason.

---

### 📄 File: [src/utils/logger.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/utils/logger.py)
**Purpose:** The "Black Box" of the project. It records every event (errors, starts, stops) so Chirag can see exactly what happened while he was away.

#### Code Breakdown:
```python
7: from loguru import logger
```
*   **What it does:** Imports a high-performance logging library.
*   **Why it exists:** Standard Python logging is complicated. `Loguru` makes it easy to add colors and save to files with one line.

```python
13: logger.add(sys.stderr, format="...", level="INFO", colorize=True)
```
*   **What it does:** Sends important messages to your terminal screen in color.
*   **Why it exists:** Helps the developer see "Live" what the app is doing.

```python
21: logger.add("logs/airshield_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days")
```
*   **What it does:** Saves all messages to a file. 
    *   `rotation="1 day"`: Creates a brand new file every morning.
    *   `retention="7 days"`: Deletes old logs after a week to save disk space.
*   **Why it exists:** If the app crashes at 3:00 AM, this file tells you why.

---

### 📄 File: [src/utils/time_utils.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/utils/time_utils.py)
**Purpose:** The "Clock Synchronizer." It ensures the app always uses Indian Time, no matter where in the world the server is.

#### Code Breakdown:
```python
6: return datetime.utcnow() + timedelta(hours=5, minutes=30)
```
*   **What it does:** Takes the "Universal Time" and manually adds 5 hours and 30 minutes to reach **Indian Standard Time (IST)**.
*   **Why it exists:** Cloud servers (like GitHub or Streamlit) run on UTC. If we don't do this, a reading taken at 10:00 PM in Delhi would be labeled "4:30 PM" on your charts.
*   **What breaks if removed:** All your graphs and "Daily Averages" will be shifted by 5.5 hours, making the data look wrong.

---

---

## 📡 Chapter 4: Data Ingestion Layer (The ETL Pipeline)

This layer is the "Front Line." Its job is to go out into the internet, grab raw data, clean it, and prepare it for the database. This process is called **ETL** (Extract, Transform, Load).

### 📄 File: [src/data/cities.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/data/cities.py)
**Purpose:** The "GPS Map." It contains the list of cities we want to track and their exact coordinates.

#### Code Breakdown:
```python
21: INDIAN_CITIES: list[CityConfig] = [
22:     CityConfig("Delhi", 28.6139, 77.2090, "delhi"),
23:     CityConfig("Mumbai", 19.0760, 72.8777, "mumbai"),
...
```
*   **What it does:** Creates a list of "City Objects." Each one stores the name, latitude, and longitude.
*   **Why it exists:** API scrapers don't understand names like "Delhi"; they need numbers (coordinates). Centralizing this list means we can add a new city by changing just *one* line of code.

---

### 📄 File: [src/data/scrapers/openweather_scraper.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/data/scrapers/openweather_scraper.py)
**Purpose:** The "Courier." It visits the OpenWeather API and brings back a package of raw air quality data.

#### Code Breakdown:
```python
15: @retry_on_failure(exceptions=(requests.exceptions.RequestException,))
```
*   **What it does:** Uses the utility we built in Chapter 3 to protect this function from network errors.
*   **Why it exists:** The internet is unstable. If this call fails, the system tries again automatically.

```python
25: response = requests.get(url, params=params, timeout=10)
```
*   **What it does:** Sends a request to the OpenWeather server. It says: "Give me the pollution for these coordinates."
*   **What breaks if removed:** We get zero data. The project stops.

```python
32: return {"city": city_name, "aqi": pollution["main"]["aqi"], "pm2_5": components.get("pm2_5"), ...}
```
*   **What it does:** Converts the messy API response into a clean Python dictionary.
*   **Why it exists:** OpenWeather sends back a lot of data we don't need. This "maps" only the important parts (PM2.5, PM10, etc.) into a format our system understands.

---

### 📄 File: [src/data/cleaner.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/data/cleaner.py)
**Purpose:** The "Filter." It ensures the data follows the rules and matches the global AQI standards.

#### Code Breakdown:
```python
12: OPENWEATHER_TO_EPA = {1: 25, 2: 75, 3: 125, 4: 175, 5: 250}
```
*   **What it does:** Converts OpenWeather's scale (1-5) to the US EPA scale (0-500).
*   **Why it exists:** OpenWeather's "5" means "Very Poor." But in India and the US, a "5" would be "Excellent." This translator ensures our dashboard shows the numbers people expect.

```python
27: required = ["city", "latitude", "longitude", "aqi", "timestamp"]
```
*   **What it does:** Checks if any critical information is missing.
*   **What happens if removed:** If an API sends back a reading without a city name, the database might crash when trying to save it. This prevents that.

---

### 📄 File: [src/data/pipeline.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/data/pipeline.py)
**Purpose:** The "Orchestrator." It manages the entire flow from Scraping → Cleaning → Saving.

#### Code Breakdown:
```python
47: def run_pipeline() -> PipelineResult:
```
*   **What it does:** This is the "Master Switch." When this function runs, the whole project wakes up.

```python
79: for name, fetch_fn, api_key in sources:
80:     data = _extract_source(name, fetch_fn, api_key)
```
*   **What it does:** Loops through different data sources (OpenWeather, AQICN).
*   **Why it exists:** **Fault Isolation.** If OpenWeather is down, the system still tries to get data from AQICN. One failure doesn't kill the whole pipeline.

```python
95: cleaned = clean_all_readings(all_readings)
99: result.saved_readings = save_readings(cleaned)
```
*   **What it does:** Sends the raw data to the `cleaner.py` and then to the `database/queries.py`.
*   **Data Flow:** Raw (API) → Processed (Cleaner) → Permanent (SQL Database).

---

---

## 🗄️ Chapter 5: Database Layer (The Memory)

This layer is the "Vault." It ensures that every piece of data we scrape is saved forever, allowing us to see historical trends and train our AI models. We use **SQLAlchemy** (an ORM) to talk to the database.

### 📄 File: [src/database/connection.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/database/connection.py)
**Purpose:** The "Tunnel." It creates the direct connection between our Python code and the database engine (SQLite or PostgreSQL).

#### Code Breakdown:
```python
13: class Base(DeclarativeBase): pass
```
*   **What it does:** This is the "Grandfather" class. 
*   **Why it exists:** Every table we create later (like `AirQualityReading`) must "inherit" from this so SQLAlchemy knows they are part of the same database system.

```python
18: engine = create_engine(settings.DATABASE_URL)
```
*   **What it does:** Starts the database engine using the URL from our config.
*   **Why it exists:** This is the actual "Driver" that knows how to speak SQL. 

```python
32: def init_db():
33:     Base.metadata.create_all(bind=engine)
```
*   **What it does:** This is the "Builder." It looks at our code models and automatically creates the SQL tables if they don't exist yet.
*   **What breaks if removed:** You'll get "Table Not Found" errors as soon as you try to save data.

---

### 📄 File: [src/database/models.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/database/models.py)
**Purpose:** The "Blueprint." It defines exactly what columns and rows our database table should have.

#### Code Breakdown:
```python
17: __tablename__ = "air_quality_readings"
```
*   **What it does:** Names the table in SQL.

```python
20: id = Column(Integer, primary_key=True, autoincrement=True)
```
*   **What it does:** Assigns a unique ID (1, 2, 3...) to every single reading.
*   **Why it exists:** We need a foolproof way to find a specific row later.

```python
23: city = Column(String, nullable=False, index=True)
```
*   **What it does:** Stores the city name. 
*   **`index=True`:** This is the **most important performance setting**. It creates a "Table of Contents" for the city column, making searches 100x faster.

```python
36: pm2_5 = Column(Float)
```
*   **What it does:** Stores the PM2.5 level as a decimal number.

```python
41: measured_at = Column(DateTime, nullable=False)
42: created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```
*   **What it does:** Tracks two different times.
    *   `measured_at`: When the pollution actually happened in the world.
    *   `created_at`: When we physically saved it to our database.
*   **Why it exists:** If our internet is down for 3 hours, we might save 3 hours of data all at once at 5:00 PM. We need to know the *actual* pollution time, not just the save time.

---

### 📄 File: [src/database/queries.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/database/queries.py)
**Purpose:** The "librarian." It handles the logic of putting books (data) on shelves and finding them later.

#### Code Breakdown:
```python
25: for data in readings:
26:     try:
27:         reading = AirQualityReading(...)
28:         session.add(reading)
29:         session.flush()
```
*   **What it does:** Loops through the cleaned data and prepares it for saving.
*   **Why it exists:** **Record-Level Fault Tolerance.** By using `try-except` *inside* the loop, if one city's data is corrupted, the other 19 cities still get saved.

```python
53: session.commit()
```
*   **What it does:** The "Final Seal." It physically writes the data to the hard drive.
*   **What breaks if removed:** The data will exist in "Memory" (RAM) but will disappear the moment the app closes.

```python
80: def get_city_readings(city: str, limit: int = 100):
```
*   **What it does:** This is the function the Dashboard uses to draw charts. It says: "Give me the last 100 hours of data for Delhi."

---

---

## 🔮 Chapter 6: ML Logic (The Oracle)

This layer is the "Brain." It doesn't just look at what is happening *now*; it uses historical patterns to predict what will happen *later*. We use **XGBoost**, a high-performance machine learning algorithm.

### 📄 File: [src/ml/feature_engineering.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/ml/feature_engineering.py)
**Purpose:** The "Translator." It turns raw data (dates and city names) into numbers that a computer can perform math on.

#### Code Breakdown:
```python
16: def add_time_features(df: pd.DataFrame):
...
32:     df["hour"] = df["measured_at"].dt.hour
33:     df["month"] = df["measured_at"].dt.month
```
*   **What it does:** Extracts the hour and month from a date (e.g., "8:00 AM on Jan 15" becomes `hour=8, month=1`).
*   **Why it exists:** Machine learning models can't read calendars. They need to know the *number* of the hour to see if pollution is always high at 8:00 AM.

```python
35:     df["is_winter"] = df["month"].isin([11, 12, 1, 2]).astype(int)
```
*   **What it does:** Creates a "Winter Flag" (1 if it's Nov-Feb, 0 otherwise).
*   **Why it exists:** In India, winter pollution behaves very differently than summer pollution due to temperature inversions. This "hint" helps the AI understand the season.

```python
51: df["city_code"] = pd.Categorical(df["city"]).codes
```
*   **What it does:** Assigns a number to each city (Delhi=0, Mumbai=1...).
*   **What breaks if removed:** The model will crash because it cannot perform multiplication on the word "Delhi."

---

### 📄 File: [src/ml/train_model.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/ml/train_model.py)
**Purpose:** The "Teacher." It shows the AI thousands of historical examples so it can learn how weather affects pollution.

#### Code Breakdown:
```python
51: model = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, ...)
```
*   **What it does:** Configures the "XGBoost Brain."
    *   `n_estimators=200`: It will look at the data in 200 different ways (trees).
    *   `max_depth=6`: It won't get *too* bogged down in tiny details (prevents memorization/overfitting).
*   **Why it exists:** This is where we define the "intelligence" level of our model.

```python
117: X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, ...)
```
*   **What it does:** Hides 20% of the data from the AI during training.
*   **Why it exists:** This is the **"Final Exam."** We train the AI on 80% of the data, then test it on the other 20% to see if it can actually predict data it hasn't seen before.

---

### 📄 File: [src/ml/predictor.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/ml/predictor.py)
**Purpose:** The "Production Engine." It takes live data from our scraper and asks the trained AI for a prediction for the next hour/day.

#### Code Breakdown:
```python
33: model = joblib.load(filepath)
```
*   **What it does:** Loads the "Learned Brain" (`.joblib` file) from the hard drive.
*   **What breaks if removed:** The app has no "intelligence." It can see the present, but it's blind to the future.

```python
110: predicted_pm2_5 = float(model.predict(features)[0])
```
*   **What it does:** THE MOMENT OF TRUTH. It feeds the current weather/city data into the brain and gets the predicted PM2.5 value.

```python
113: predicted_pm2_5 = max(0, min(predicted_pm2_5, 500))
```
*   **What it does:** **Safety Rails.** It ensures the AI doesn't hallucinate a negative number (impossible) or a number like 1,000,000 (unrealistic). It "clamps" the answer to a human-readable scale.

---

---

## 🤖 Chapter 7: Agentic Brain (The AI Advisor)

This layer is the "Voice." It takes the mathematical numbers from our scraper and ML model and turns them into human-readable health advice. It uses **OpenRouter** to access the world's most advanced Large Language Models (LLMs).

### 📄 File: [src/agent/advisor.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/agent/advisor.py)
**Purpose:** The "Digital Doctor." It builds "Reality Context" for the AI and manages the conversation.

#### Code Breakdown:
```python
20: FREE_MODELS = [
21:     "nvidia/nemotron-3-nano-30b-a3b:free",
22:     "openrouter/free",
...
26: ]
```
*   **What it does:** Defines a "Cascade" of AI models.
*   **Why it exists:** **Resilience.** If the primary model (Nemotron) is busy or rate-limited, the agent doesn't give up. It automatically tries the next one (Llama, Gemma, etc.) until it gets an answer.

```python
60: def _build_context(self):
```
*   **What it does:** This is the most complex function in the file. It gathers:
    1.  Live data from the API.
    2.  Predictions for the next 7 days from our ML model.
*   **Why it exists:** An AI is only as smart as the data you give it. This function creates a "Data Snapshot" so the AI knows exactly what the pollution looks like in your city today and next week.

```python
117: system_prompt = (
118:     "You are the AirShield AI Health Advisor... "
123:     "ALWAYS calculate and state the EXACT percentage change..."
131: )
```
*   **What it does:** Sets the "Rules of Engagement" for the AI. It tells the AI to be analytical, use precise numbers, and never lie about the date.
*   **Why it exists:** Without this, the AI might just give generic advice. This forces it to act like a specialized Data Scientist/Doctor.

```python
142: for model_name in FREE_MODELS:
155:     response = requests.post("https://openrouter.ai/api/v1/chat/completions", ...)
```
*   **What it does:** Sends the data and the user's question to the cloud.
*   **What breaks if removed:** The "AI Advisor" tab in the dashboard will be empty. The system will have data but won't be able to explain it.

```python
168: if response.status_code == 429:
169:     time.sleep(3)
170:     continue
```
*   **What it does:** Handles "High Traffic" errors (Rate Limiting). If the AI server says "Too many requests," our agent waits 3 seconds and tries again.

---

---

## 🖥️ Chapter 8 & 9: Backend & Frontend (The Face)

This layer is the "Skin." It turns all the complex math, SQL queries, and AI logic into a beautiful, clickable website. We use **Streamlit** for the UI, **Folium** for maps, and **Plotly** for charts.

### 📄 File: [dashboard/app.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/dashboard/app.py)
**Purpose:** The "Homepage." It shows a live map of India with real-time pollution bubbles for all 20 cities.

#### Code Breakdown:
```python
26: st.set_page_config(page_title="AirShield AI", layout="wide")
```
*   **What it does:** Configures the browser tab and makes the website use the full width of the screen.
*   **Why it exists:** Professional dashboards need space for maps and side-by-side metrics.

```python
66: @st.cache_data(ttl=300)
67: def fetch_live_data():
```
*   **What it does:** This is the **most important performance optimization**. It tells the website: "If a user refreshes the page within 5 minutes, don't waste time calling the API again; just show the data we already have."
*   **What breaks if removed:** Every time a user clicks a button, the app will make 20 API calls, hitting "Rate Limits" instantly and making the site feel very slow.

```python
85: india_map = folium.Map(location=[22.5, 78.5], zoom_start=5, tiles="CartoDB dark_matter")
```
*   **What it does:** Creates the interactive map of India with a "Dark Mode" aesthetic.

```python
114: folium.CircleMarker(..., radius=max(10, min(40, 10 + aqi // 10)), color=color, ...)
```
*   **What it does:** Draws the AQI bubbles. 
    *   **Radius:** The bubbles get physically bigger as the air gets worse (visual warning).
    *   **Color:** The color changes from Green to Red based on the AQI scale.

---

### 📄 File: [dashboard/pages/1_📈_Forecast.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/dashboard/pages/1_📈_Forecast.py)
**Purpose:** The "Prophet." It uses the ML model to generate a 24-hour hourly forecast.

#### Code Breakdown:
```python
44: for h_offset in range(0, 24):
50:     result = predict_pm25(..., hour=future_time.hour, ...)
```
*   **What it does:** A "Time Loop." It asks the ML model: "What will the air be at 1 PM? 2 PM? 3 PM?" until it has a full day's worth of data.
*   **Why it exists:** Humans need to plan. This allows a user to see that pollution peaks at 8:00 PM, so they should go for their walk earlier.

```python
78: fig = go.Figure()
90: fig.add_trace(go.Scatter(x=times, y=values, mode="lines+markers", ...))
```
*   **What it does:** Uses **Plotly** to draw the interactive line chart. Unlike a static image, users can hover over these points to see exact values.

---

### 📄 File: [dashboard/pages/2_🏙️_Compare.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/dashboard/pages/2_🏙️_Compare.py)
**Purpose:** The "Ranker." It lets users select multiple cities to see which one has the cleanest air.

#### Code Breakdown:
```python
130: ranked = sorted(selected_data, key=lambda d: d.get("pm2_5", 0))
```
*   **What it does:** Sorts the list of cities from lowest PM2.5 (cleanest) to highest (most polluted).
*   **Why it exists:** Gamification. Users want to see how their city ranks against others (e.g., "Is Mumbai cleaner than Delhi today?").

---

### 📄 File: [dashboard/pages/3_🤖_AI_Advisor.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/dashboard/pages/3_🤖_AI_Advisor.py)
**Purpose:** The "Chat Center." A user-friendly interface for the AI Advisor we built in Chapter 7.

#### Code Breakdown:
```python
49: if "messages" not in st.session_state:
50:     st.session_state.messages = []
```
*   **What it does:** Creates a "Memory" for the chat.
*   **Why it exists:** Streamlit "reruns" the whole script on every click. These lines ensure the chat history doesn't disappear when you send a message.

```python
71: response = agent.ask(prompt)
```
*   **What it does:** Sends the user's chat message to the Agentic Brain (Chapter 7) and displays the doctor's advice.

---

---

## ☁️ Chapter 10: Automation & CI-CD (The Ghost)

This layer is the "Heartbeat." It ensures the project stays alive 24/7 without Chirag having to turn his computer on. It automates the scraping process using **GitHub Actions** (in the cloud) or **APScheduler** (if running via Docker).

### 📄 File: [.github/workflows/scrape.yml](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/.github/workflows/scrape.yml)
**Purpose:** The "Cloud Robot." It tells GitHub's servers to wake up every hour and run our scrapers for free.

#### Code Breakdown:
```yaml
6: - cron: '0 * * * *'
```
*   **What it does:** This is a **Cron Job**. It tells GitHub: "Run this script exactly at the start of every hour (1:00, 2:00, 3:00...)."
*   **Why it exists:** Air pollution changes constantly. Hourly updates ensure our dashboard and AI Advisor are always talking about the *current* situation.

```yaml
11: runs-on: ubuntu-latest
```
*   **What it does:** Spawns a virtual Linux computer in GitHub's cloud. 

```yaml
28: OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
```
*   **What it does:** Injects your API keys into the virtual computer. 
*   **Why it exists:** Security. You save your keys in GitHub's "Secrets" vault so nobody can see them in the code, but the robot can still use them to scrape data.

---

### 📄 File: [scheduler/jobs.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/scheduler/jobs.py)
**Purpose:** The "Local Timer." If you run the project on your own server using Docker, this file manages the 1-hour heartbeat.

#### Code Breakdown:
```python
17: scheduler = BlockingScheduler()
20: scheduler.add_job(run_pipeline, trigger="interval", minutes=60, ...)
```
*   **What it does:** Creates a timer that waits 60 minutes, runs the `pipeline.py`, and then repeats forever.

```python
36: run_pipeline()  # first run
```
*   **What it does:** Runs the scraper immediately as soon as you start the app.
*   **Why it exists:** If the app starts up at 10:05 AM, we don't want to wait until 11:00 AM for the first piece of data. This ensures the dashboard is populated instantly.

---

---

## 📚 Chapter 11: Seeding & History (The Foundation)

Before the app could predict anything, it needed to learn from the past. These files handle the massive 5-year Kaggle dataset used to train the "Brain."

### 📄 File: [src/data/historical_cleaner.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/data/historical_cleaner.py)
**Purpose:** The "Filter." It takes a dirty raw CSV and makes it perfect for Machine Learning.

#### Code Breakdown:
```python
42: cols_to_drop = ["Benzene", "Toluene", "Xylene", "AQI_Bucket", "NOx"]
```
*   **What it does:** Removes chemicals that our live APIs don't track.
*   **Why it exists:** If we train the AI to care about "Benzene," but our live scraper can't find Benzene, the AI will get confused and fail in production. This ensures the "Training Reality" matches the "Live Reality."

```python
61: df = df[(df["AQI"].isna()) | ((df["AQI"] >= 0) & (df["AQI"] <= 500))]
```
*   **What it does:** Deletes rows where the sensor glitched (e.g., AQI = 999).
*   **Why it exists:** **"Garbage In, Garbage Out."** If we teach the AI that 999 is a normal number, it will make wild, incorrect predictions.

---

### 📄 File: [src/data/historical_loader.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/data/historical_loader.py)
**Purpose:** The "Importer." It moves the cleaned CSV data into our SQL database in bulk.

#### Code Breakdown:
```python
41: BATCH_SIZE = 5000
112: session.bulk_save_objects(records)
```
*   **What it does:** Inserts 5,000 rows at a time instead of 1 by 1.
*   **Why it exists:** Saving 100,000 rows one by one would take 30 minutes. In "Batches," it takes 30 seconds.

---

## 🧪 Chapter 12: Model Comparison (The Science)

We didn't just pick XGBoost by accident. We ran a "Tournament" between different AI models to see which one was the most accurate.

### 📄 File: [src/ml/model_comparison.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/ml/model_comparison.py)
**Purpose:** The "Referee." It trains 4 different models and picks the winner.

#### Code Breakdown:
```python
63: models = {
64:     "Linear Regression": LinearRegression(),
66:     "Random Forest": RandomForestRegressor(...),
73:     "XGBoost": xgb.XGBRegressor(...),
84:     "LightGBM": lgb.LGBMRegressor(...),
94: }
```
*   **What it does:** Defines the "Contestants."
*   **Why it exists:** High-level engineering requires proof. This script proves that XGBoost is better for this specific air quality data than a simple Random Forest or Linear Regression.

```python
110: best = max(results, key=lambda x: x["r2"])
```
*   **What it does:** Selects the model with the highest **R² Score** (the most "accurate" one).

---

## 📡 Chapter 13: Secondary Scraper (The Backup)

### 📄 File: [src/data/scrapers/aqicn_scraper.py](file:///c:/Users/Chirag/OneDrive/Desktop/AI_PROJECT/src/data/scrapers/aqicn_scraper.py)
**Purpose:** The "Alternative Link." It scrapes data from **AQICN.org** instead of OpenWeatherMap.

#### Code Breakdown:
```python
22: url = f"https://api.waqi.info/feed/{city_slug}/"
```
*   **What it does:** Connects to the World Air Quality Index project.
*   **Why it exists:** If OpenWeatherMap changes their terms or goes down, AirShield AI can switch to this source with a single line of code in the pipeline.

---

## 🔄 Chapter 14: The End-to-End Data Flow (The Grand Unified View)

Here is exactly how a single piece of air pollution data travels through your system:

1.  **Trigger:** GitHub Actions wakes up at 1:00 PM.
2.  **Extraction:** `pipeline.py` calls `openweather_scraper.py`. The scraper visits the API and gets a JSON response for all 20 cities.
3.  **Transformation:** `cleaner.py` checks if the data is valid and converts the 1-5 scale into the 0-500 scale.
4.  **Loading:** `queries.py` saves the 20 new rows into the **PostgreSQL (Supabase)** database.
5.  **Intelligence:** The user opens the Dashboard. `app.py` pulls the latest data and calls `predictor.py`.
6.  **Prediction:** The XGBoost model artifact (`.joblib`) analyzes the current weather and generates a 7-day forecast.
7.  **Reasoning:** The `advisor.py` feeds the Forecast + Live Data into an LLM (Nemotron-30B).
8.  **Output:** The LLM returns a personalized health report (e.g., "Delhi is getting 20% worse tomorrow, wear a mask!").

---

## 🏛️ Chapter 15: Final Architecture Summary

1.  **Frontend:** Streamlit + Folium + Plotly (Visual Intelligence)
2.  **ML Model:** XGBoost Regressor (Predictive Intelligence)
3.  **AI Engine:** LLM Agent via OpenRouter (Generative Intelligence)
4.  **Database:** PostgreSQL/Supabase (Historical Memory)
5.  **Automation:** GitHub Actions + APScheduler (Operational Continuity)

---

## 🛠️ Chapter 16: Critical Design Decisions (The "Why")

*   **Why Pydantic?** To ensure the app crashes *early* with a clear error message if a setting is wrong, instead of behaving weirdly later.
*   **Why caching (`@st.cache_data`)?** To prevent burning your API keys and making the UI feel "snappy."
*   **Why fault isolation in the Pipeline?** So that if one API key expires, the other one still populates the dashboard.
*   **Why local model loading in `predictor.py`?** To make predictions happen in milliseconds (locally) instead of seconds (via an external ML API).

---

## 🚀 Chapter 17: Possible Improvements for Version 2.0

1.  **Satellite Vision:** Integrate NASA/ESA satellite data for cities where ground sensors are broken.
2.  **Email Alerts:** Add a feature to email users if PM2.5 is predicted to cross 200 μg/m³.
3.  **Edge Training:** Implement a weekly automated "Retraining" job where the model learns from the *new* data stored in the database.

---

**Congratulations, Chirag. You have successfully deconstructed the complete AirShield AI Technical Blueprint.**
