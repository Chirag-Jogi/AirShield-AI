from datetime import datetime, timedelta, timezone
from typing import Optional

def get_ist_now():
    """Returns the current time in Indian Standard Time (UTC+5:30)."""
    # Streamlit Cloud servers use UTC. India is UTC + 5.5 hours.
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def to_naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Elite Time Sanitizer:
    Ensures a datetime object is in UTC and has NO timezone label (naive).
    This is required for PostgreSQL 'TIMESTAMP WITHOUT TIME ZONE' columns.
    """
    if dt is None:
        return None
    
    # If it has a timezone, convert to UTC and then strip it
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    
    return dt
