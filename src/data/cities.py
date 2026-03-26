"""
City Configuration — Single source of truth for all target cities.

Both scrapers import from here instead of maintaining duplicate lists.
Add/remove cities here and ALL scrapers update automatically.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CityConfig:
    """Immutable city configuration."""
    name: str
    latitude: float
    longitude: float
    aqicn_slug: str  # city identifier for AQICN API


# All target cities. Modify this list to change scraping targets.
INDIAN_CITIES: list[CityConfig] = [
    CityConfig("Delhi", 28.6139, 77.2090, "delhi"),
    CityConfig("Mumbai", 19.0760, 72.8777, "mumbai"),
    CityConfig("Bangalore", 12.9716, 77.5946, "bangalore"),
    CityConfig("Kolkata", 22.5726, 88.3639, "kolkata"),
    CityConfig("Chennai", 13.0827, 80.2707, "chennai"),
    CityConfig("Hyderabad", 17.3850, 78.4867, "hyderabad"),
    CityConfig("Pune", 18.5204, 73.8567, "pune"),
    CityConfig("Ahmedabad", 23.0225, 72.5714, "ahmedabad"),
    CityConfig("Lucknow", 26.8467, 80.9462, "lucknow"),
    CityConfig("Jaipur", 26.9124, 75.7873, "jaipur"),
]
