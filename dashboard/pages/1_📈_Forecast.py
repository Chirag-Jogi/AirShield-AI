"""
Page 2: 24-Hour Forecast
Shows predicted PM2.5 for each hour of the day.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.cities import INDIAN_CITIES
from src.ml.predictor import predict_pm25
from src.data.scrapers import openweather_scraper
from config import settings


st.set_page_config(page_title="Forecast | AirShield AI", page_icon="📈", layout="wide")


@st.cache_data(ttl=300)
def fetch_city_live(city_name: str):
    """Fetch live data for one city."""
    city = next((c for c in INDIAN_CITIES if c.name == city_name), None)
    if not city or not settings.OPENWEATHER_API_KEY:
        return None
    return openweather_scraper.fetch_air_quality(
        settings.OPENWEATHER_API_KEY, city.name, city.latitude, city.longitude
    )


def generate_24h_forecast(city: str, live_data: dict) -> list:
    """
    Generate predictions for next 24 hours.
    Uses current live pollutant values as base inputs.
    Only changes hour/month for each prediction.
    """
    now = datetime.now()
    forecasts = []

    for h_offset in range(0, 24):
        future_time = now + timedelta(hours=h_offset)
        hour = future_time.hour
        month = future_time.month
        day_of_week = future_time.weekday()

        result = predict_pm25(
            city=city,
            hour=hour,
            month=month,
            day_of_week=day_of_week,
            no2=live_data.get("no2") if live_data else None,
            co=live_data.get("co") if live_data else None,
            pm10=live_data.get("pm10") if live_data else None,
            so2=live_data.get("so2") if live_data else None,
            o3=live_data.get("o3") if live_data else None,
            nh3=live_data.get("nh3") if live_data else None,
        )

        forecasts.append({
            "time": future_time.strftime("%I %p"),
            "hour": hour,
            "pm25": result["predicted_pm25"],
            "is_now": h_offset == 0,
        })

    return forecasts


def create_forecast_chart(forecasts: list, live_pm25: float, city: str):
    """Create a Plotly chart showing 24-hour forecast."""
    times = [f["time"] for f in forecasts]
    values = [f["pm25"] for f in forecasts]

    fig = go.Figure()

    # Current hour (live value)
    fig.add_trace(go.Scatter(
        x=[times[0]],
        y=[live_pm25],
        mode="markers",
        marker=dict(size=15, color="lime", symbol="star"),
        name="📡 Live Now",
    ))

    # Predicted line
    fig.add_trace(go.Scatter(
        x=times,
        y=values,
        mode="lines+markers",
        line=dict(color="orange", width=3, dash="dash"),
        marker=dict(size=6),
        name="🔮 Predicted",
        fill="tozeroy",
        fillcolor="rgba(255,165,0,0.1)",
    ))

    # WHO safe line
    fig.add_hline(y=25, line_dash="dot", line_color="green",
                  annotation_text="WHO Safe (25)")

    # India standard line
    fig.add_hline(y=60, line_dash="dot", line_color="yellow",
                  annotation_text="India Std (60)")

    # Danger line
    fig.add_hline(y=120, line_dash="dot", line_color="red",
                  annotation_text="Unhealthy (120)")

    fig.update_layout(
        title=f"24-Hour PM2.5 Forecast for {city}",
        xaxis_title="Time",
        yaxis_title="PM2.5 (μg/m³)",
        height=450,
        template="plotly_dark",
        legend=dict(x=0, y=1.15, orientation="h"),
    )

    return fig


def main():
    st.title("📈 24-Hour Air Quality Forecast")
    st.markdown("**See what's coming — plan your day around the air quality**")
    st.markdown("---")

    # City selector
    city_names = [city.name for city in INDIAN_CITIES]
    selected = st.selectbox("🏙️ Select City:", city_names, index=0)

    # Fetch live data
    with st.spinner(f"📡 Fetching live data for {selected}..."):
        live_data = fetch_city_live(selected)

    live_pm25 = live_data.get("pm2_5", 0) if live_data else 0

    # Calculate real AQI from PM2.5 (US EPA standard — matches IQAir, AQI.in, etc.)
    def pm25_to_aqi(pm25):
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

    real_aqi, aqi_text = pm25_to_aqi(live_pm25)
    st.markdown(f"### 📡 Live: AQI = **{real_aqi}** ({aqi_text}) | PM2.5 = **{live_pm25:.1f}** μg/m³")

    # Generate forecast
    forecasts = generate_24h_forecast(selected, live_data)

    # Chart
    fig = create_forecast_chart(forecasts, live_pm25, selected)
    st.plotly_chart(fig)

    # Key insights
    st.markdown("---")
    st.subheader("💡 Key Insights")

    best_hour = min(forecasts, key=lambda x: x["pm25"])
    worst_hour = max(forecasts, key=lambda x: x["pm25"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📡 Live AQI", f"{real_aqi}")
        st.metric("📡 Live PM2.5", f"{live_pm25:.1f} μg/m³")

    with col2:
        st.success(f"✅ **Best time to go out:** {best_hour['time']}\n\n"
                   f"Predicted PM2.5: {best_hour['pm25']} μg/m³")

    with col3:
        st.error(f"❌ **Worst time:** {worst_hour['time']}\n\n"
                 f"Predicted PM2.5: {worst_hour['pm25']} μg/m³")

    # Hourly breakdown table
    st.markdown("---")
    st.subheader("📋 Hour-by-Hour Breakdown")

    for f in forecasts:
        pm = f["pm25"]
        if pm <= 30:
            emoji = "🟢"
        elif pm <= 60:
            emoji = "🟡"
        elif pm <= 120:
            emoji = "🟠"
        else:
            emoji = "🔴"

        label = "📡 NOW" if f["is_now"] else "🔮"
        value = live_pm25 if f["is_now"] else pm
        st.markdown(f"{emoji} **{f['time']}** — {label} PM2.5: **{value:.1f}** μg/m³")

    # Footer
    st.markdown("---")
    st.caption("Predictions based on XGBoost model trained on 5+ years of historical data. "
               "Actual values may vary due to weather changes and unexpected events.")


if __name__ == "__main__":
    main()
