"""
Page 3: City Comparison
Compare air quality across multiple cities side-by-side.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.cities import INDIAN_CITIES
from src.data.scrapers import openweather_scraper
from config import settings


st.set_page_config(page_title="Compare Cities | AirShield AI", page_icon="🏙️", layout="wide")


@st.cache_data(ttl=300)
def fetch_all_cities():
    """Fetch live data for all cities."""
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


def pm25_to_aqi(pm25):
    """Convert PM2.5 to US EPA AQI."""
    breakpoints = [
        (0.0, 12.0, 0, 50, "Good 🟢"),
        (12.1, 35.4, 51, 100, "Moderate 🟡"),
        (35.5, 55.4, 101, 150, "Unhealthy (Sensitive) 🟠"),
        (55.5, 150.4, 151, 200, "Unhealthy 🔴"),
        (150.5, 250.4, 201, 300, "Very Unhealthy 🟤"),
        (250.5, 500.0, 301, 500, "Hazardous ☠️"),
    ]
    for bp_lo, bp_hi, aqi_lo, aqi_hi, label in breakpoints:
        if pm25 <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return int(aqi), label
    return 500, "Hazardous ☠️"


def main():
    st.title("🏙️ City Comparison")
    st.markdown("**Compare air quality across Indian cities — who breathes the cleanest air?**")
    st.markdown("---")

    # Fetch live data for all cities
    with st.spinner("📡 Fetching live data for all cities..."):
        all_data = fetch_all_cities()

    if not all_data:
        st.error("❌ Could not fetch live data. Check API key.")
        return

    # City selector (multi-select)
    city_names = [d["city"] for d in all_data]
    selected_cities = st.multiselect(
        "Select cities to compare (2-10):",
        city_names,
        default=city_names[:5],  # Default: first 5 cities
    )

    if len(selected_cities) < 2:
        st.warning("⚠️ Please select at least 2 cities to compare.")
        return

    # Filter data for selected cities
    selected_data = [d for d in all_data if d["city"] in selected_cities]

    # --- Bar Chart: PM2.5 Comparison ---
    st.subheader("📊 PM2.5 Comparison")

    cities = [d["city"] for d in selected_data]
    pm25_values = [d.get("pm2_5", 0) for d in selected_data]
    aqi_values = [pm25_to_aqi(pm)[0] for pm in pm25_values]

    # Color bars based on AQI level
    colors = []
    for pm in pm25_values:
        if pm <= 12:
            colors.append("#00e400")
        elif pm <= 35.4:
            colors.append("#ffff00")
        elif pm <= 55.4:
            colors.append("#ff7e00")
        elif pm <= 150.4:
            colors.append("#ff0000")
        else:
            colors.append("#8f3f97")

    fig = go.Figure(data=[
        go.Bar(
            x=cities,
            y=pm25_values,
            marker_color=colors,
            text=[f"{v:.1f}" for v in pm25_values],
            textposition="outside",
        )
    ])

    fig.add_hline(y=12, line_dash="dot", line_color="green",
                  annotation_text="WHO Safe (12)")
    fig.add_hline(y=35.4, line_dash="dot", line_color="yellow",
                  annotation_text="US Moderate (35)")

    fig.update_layout(
        yaxis_title="PM2.5 (μg/m³)",
        height=400,
        template="plotly_dark",
    )
    st.plotly_chart(fig)

    # --- AQI Ranking ---
    st.markdown("---")
    st.subheader("🏆 City Ranking (Best to Worst)")

    # Sort by PM2.5 (lowest = cleanest)
    ranked = sorted(selected_data, key=lambda d: d.get("pm2_5", 0))

    for i, data in enumerate(ranked):
        city = data["city"]
        pm25 = data.get("pm2_5", 0)
        aqi, label = pm25_to_aqi(pm25)
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"

        st.markdown(
            f"{medal} **{city}** — AQI: **{aqi}** ({label}) | "
            f"PM2.5: {pm25:.1f} μg/m³"
        )

    # --- Pollutant Comparison Table ---
    st.markdown("---")
    st.subheader("🧪 Detailed Pollutant Comparison")

    table_data = []
    for data in selected_data:
        aqi, label = pm25_to_aqi(data.get("pm2_5", 0))
        table_data.append({
            "City": data["city"],
            "AQI": aqi,
            "PM2.5": round(data.get("pm2_5", 0), 1),
            "PM10": round(data.get("pm10", 0), 1),
            "NO₂": round(data.get("no2", 0), 1),
            "CO": round(data.get("co", 0), 1),
            "O₃": round(data.get("o3", 0), 1),
            "SO₂": round(data.get("so2", 0), 1),
        })

    st.dataframe(table_data)

    # --- Key Insight ---
    st.markdown("---")
    cleanest = ranked[0]
    dirtiest = ranked[-1]

    col1, col2 = st.columns(2)
    with col1:
        st.success(
            f"🏆 **Cleanest City: {cleanest['city']}**\n\n"
            f"PM2.5: {cleanest.get('pm2_5', 0):.1f} μg/m³"
        )
    with col2:
        st.error(
            f"⚠️ **Most Polluted: {dirtiest['city']}**\n\n"
            f"PM2.5: {dirtiest.get('pm2_5', 0):.1f} μg/m³"
        )

    # Footer
    st.markdown("---")
    st.caption("Data from OpenWeatherMap API. Updated every 5 minutes.")


if __name__ == "__main__":
    main()
