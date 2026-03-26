from datetime import datetime, timedelta

def get_ist_now():
    """Returns the current time in Indian Standard Time (UTC+5:30)."""
    # Streamlit Cloud servers use UTC. India is UTC + 5.5 hours.
    return datetime.utcnow() + timedelta(hours=5, minutes=30)
