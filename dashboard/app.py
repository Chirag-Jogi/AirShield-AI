"""
AirShield AI — Live Dashboard
Homepage with interactive map showing real-time AQI for all cities.

Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
import time

# Add project root to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from src.data.cities import INDIAN_CITIES
from src.data.scrapers import openweather_scraper
from src.ml.predictor import predict_pm25


# --- Page Config ---
st.set_page_config(
    page_title="AirShield AI",
    page_icon="🛡️",
    layout="wide",
)


def pm25_to_aqi(pm25: float) -> tuple:
    """Convert PM2.5 to US EPA AQI (0-500 scale). Returns (aqi, label, color)."""
    breakpoints = [
        (0.0, 12.0, 0, 50, "Good 🟢", "#00e400"),
        (12.1, 35.4, 51, 100, "Moderate 🟡", "#ffff00"),
        (35.5, 55.4, 101, 150, "Unhealthy (Sensitive) 🟠", "#ff7e00"),
        (55.5, 150.4, 151, 200, "Unhealthy 🔴", "#ff0000"),
        (150.5, 250.4, 201, 300, "Very Unhealthy 🟤", "#8f3f97"),
        (250.5, 500.0, 301, 500, "Hazardous ☠️", "#7e0023"),
    ]
    for bp_lo, bp_hi, aqi_lo, aqi_hi, label, color in breakpoints:
        if pm25 <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return int(aqi), label, color
    return 500, "Hazardous ☠️", "#7e0023"


def get_aqi_advice(aqi: int) -> str:
    """Return health advice based on AQI."""
    if aqi <= 50:
        return "Air is clean! Enjoy outdoors."
    elif aqi <= 100:
        return "Acceptable. Sensitive people take care."
    elif aqi <= 150:
        return "Limit prolonged outdoor exercise."
    elif aqi <= 200:
        return "Wear a mask outdoors. Avoid heavy activity."
    elif aqi <= 300:
        return "Avoid going outside. Keep windows closed."
    else:
        return "EMERGENCY! Stay indoors. Use N95 mask."


@st.cache_data(ttl=300)  # Cache for 5 minutes (300 seconds)
def fetch_live_data():
    """Fetch live AQI from OpenWeatherMap for all cities. Cached 5 min."""
    if not settings.OPENWEATHER_API_KEY:
        return []

    results = []
    for city in INDIAN_CITIES:
        data = openweather_scraper.fetch_air_quality(
            settings.OPENWEATHER_API_KEY, city.name, city.latitude, city.longitude
        )
        if data:
            results.append(data)
    return results


def create_map(live_data: list) -> folium.Map:
    """Create an interactive India map with AQI markers."""
    # Center on India
    india_map = folium.Map(
        location=[22.5, 78.5],
        zoom_start=5,
        tiles="CartoDB dark_matter",
    )

    for data in live_data:
        city = data["city"]
        pm25 = data.get("pm2_5", 0)
        aqi, label, color = pm25_to_aqi(pm25)

        # Popup content (shown on click)
        popup_html = f"""
        <div style="width:220px; font-family:Arial;">
            <h3 style="margin:0;">{city}</h3>
            <hr style="margin:5px 0;">
            <b>AQI:</b> {aqi} ({label})<br>
            <b>PM2.5:</b> {pm25:.1f} μg/m³<br>
            <b>PM10:</b> {data.get('pm10', 'N/A')}<br>
            <b>NO₂:</b> {data.get('no2', 'N/A')}<br>
            <b>CO:</b> {data.get('co', 'N/A')}<br>
            <b>O₃:</b> {data.get('o3', 'N/A')}<br>
            <b>SO₂:</b> {data.get('so2', 'N/A')}<br>
        </div>
        """

        # Scale radius based on AQI (bigger = worse)
        radius = max(10, min(40, 10 + aqi // 10))

        folium.CircleMarker(
            location=[data["latitude"], data["longitude"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{city}: AQI {aqi}",
        ).add_to(india_map)

    return india_map


def main():
    # --- Header ---
    st.title("🛡️ AirShield AI")
    st.markdown("**Real-time Air Quality Monitoring & Prediction for India**")

    # --- Fetch Live Data ---
    with st.spinner("📡 Fetching live air quality data..."):
        live_data = fetch_live_data()

    if not live_data:
        st.error("❌ Could not fetch live data. Check your OPENWEATHER_API_KEY in .env")
        return

    # --- Last Updated ---
    st.markdown(
        f"<p style='text-align:right; color:gray;'>🔄 Last updated: "
        f"{datetime.now().strftime('%I:%M %p')} | "
        f"Auto-refreshes every 5 minutes</p>",
        unsafe_allow_html=True,
    )

    # --- Map ---
    st.subheader("🗺️ Live Air Quality Map")
    india_map = create_map(live_data)
    st_folium(india_map, width=None, height=500)

    st.markdown("🟢 Good | 🟡 Fair | 🟠 Moderate | 🔴 Poor | 🟤 Very Poor")
    st.markdown("---")

    # --- City Cards ---
    st.subheader("🏙️ All Cities — Current Status")

    # Display in rows of 3
    for i in range(0, len(live_data), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(live_data):
                break

            data = live_data[idx]
            city = data["city"]
            pm25 = data.get("pm2_5", 0)
            aqi, label, color = pm25_to_aqi(pm25)

            with col:
                st.markdown(
                    f"<div style='background-color:{color}; padding:15px; "
                    f"border-radius:10px; margin-bottom:10px; text-align:center;'>"
                    f"<h3 style='margin:0; color:black;'>{city}</h3>"
                    f"<p style='margin:5px 0; color:black; font-size:24px;'>"
                    f"<b>AQI: {aqi}</b></p>"
                    f"<p style='margin:0; color:black;'>PM2.5: {pm25:.1f} | {label}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # --- Selected City Details ---
    st.markdown("---")
    st.subheader("🔍 City Details + AI Prediction")

    city_names = [d["city"] for d in live_data]
    selected = st.selectbox("Select a city for detailed analysis:", city_names)

    # Find selected city's live data
    city_data = next(d for d in live_data if d["city"] == selected)
    pm25_live = city_data.get("pm2_5", 0)

    # Get AI prediction
    prediction = predict_pm25(
        city=selected,
        no2=city_data.get("no2"),
        co=city_data.get("co"),
        pm10=city_data.get("pm10"),
        so2=city_data.get("so2"),
        o3=city_data.get("o3"),
        nh3=city_data.get("nh3"),
    )
    predicted_pm25 = prediction["predicted_pm25"]
    live_aqi, live_label, _ = pm25_to_aqi(pm25_live)
    pred_aqi, pred_label, _ = pm25_to_aqi(predicted_pm25)
    advice = get_aqi_advice(live_aqi)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📡 Live AQI", f"{live_aqi}")
        st.caption(f"PM2.5: {pm25_live:.1f} μg/m³ | {live_label}")
    with col2:
        st.metric("🔮 Predicted PM2.5", f"{predicted_pm25} μg/m³")
        st.caption(f"Predicted AQI: {pred_aqi} | {pred_label}")
    with col3:
        st.metric("📊 Air Quality", f"{live_label.split()[0]}")

    # Health Advisory
    st.info(f"🏥 **Health Advisory for {selected}:** {advice}")

    # All pollutants table
    st.markdown("**Current Pollutant Levels:**")
    pollutant_data = {
        "Pollutant": ["PM2.5", "PM10", "NO₂", "CO", "O₃", "SO₂", "NH₃"],
        "Value (μg/m³)": [
            f"{city_data.get('pm2_5', 'N/A')}",
            f"{city_data.get('pm10', 'N/A')}",
            f"{city_data.get('no2', 'N/A')}",
            f"{city_data.get('co', 'N/A')}",
            f"{city_data.get('o3', 'N/A')}",
            f"{city_data.get('so2', 'N/A')}",
            f"{city_data.get('nh3', 'N/A')}",
        ],
    }
    st.table(pollutant_data)

    # --- Footer ---
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:gray;'>"
        "🛡️ AirShield AI | Powered by XGBoost (R² = 0.775) | "
        "Live data from OpenWeatherMap"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
