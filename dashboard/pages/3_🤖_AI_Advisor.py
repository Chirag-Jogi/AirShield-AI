"""
Page 4: AI Health Advisor
Chat interface powered by the AirShield Agent (uses OpenRouter free models with fallback).
"""

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.cities import INDIAN_CITIES
from src.agent.advisor import AirShieldAgent


st.set_page_config(page_title="AI Advisor | AirShield AI", page_icon="🤖", layout="wide")


# Cache the agent instance so we don't fetch context on every single UI refresh
@st.cache_resource(ttl=300)
def get_agent(city_name: str) -> AirShieldAgent:
    with st.spinner(f"Loading environment context for {city_name}..."):
        return AirShieldAgent(city_name)


def main():
    st.title("🤖 AI Health Advisor (7-Day Outlook)")
    st.markdown("**Personalized health advice based on real-time data and 7-Day ML Predictions.**")
    st.markdown("---")

    # --- Sidebar setup ---
    st.sidebar.header("🌍 Your Location Context")
    city_names = [city.name for city in INDIAN_CITIES]
    selected_city = st.sidebar.selectbox("City:", city_names, index=0)

    # Load agent
    agent = get_agent(selected_city)
        
    if not agent.ready:
        st.error("Failed to load environment context. Check your API keys.")
        return
        
    st.sidebar.markdown(f"**Live AQI:** {agent.live_aqi} ({agent.live_label})")
    st.sidebar.markdown(f"**PM2.5:** {agent.live_pm25:.1f} μg/m³")
    st.sidebar.markdown("---")
    st.sidebar.caption("The AI has been fed this live data and the upcoming 7-day predictions for your city.")

    # --- Chat Interface ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Reset chat if city changes (this requires tracking the last city)
    if "last_city" not in st.session_state or st.session_state.last_city != selected_city:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hi! I'm your AirShield Advisor. I see you are tracking **{selected_city}**. The current AQI is **{agent.live_aqi}**. I also have the PM2.5 predictions for the next 7 days! How can I help you plan?"}
        ]
        st.session_state.last_city = selected_city

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question (e.g., 'What is the best day to jog next week?')"):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display AI message
        with st.chat_message("assistant"):
            with st.spinner("Analyzing 7-day forecast and consulting AI..."):
                response = agent.ask(prompt)
            st.markdown(response)
            
        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.pop("last_city", None)
        st.rerun()


if __name__ == "__main__":
    main()
