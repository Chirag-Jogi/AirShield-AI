"""
Elite AQI Calculator 🛡️📈
Converts raw pollutant concentrations (μg/m³) into the standard 0-500 AQI scale.
Formula based on US EPA (Environmental Protection Agency) Linear Interpolation.
"""

def calculate_us_aqi(pm25: float) -> int:
    """
    Elite PM2.5 to AQI Converter (0-500 scale).
    Standard breakpoints for PM2.5:
    """
    if pm25 is None or pm25 < 0:
        return 0

    # Breakpoints for PM2.5 (C_low, C_high, I_low, I_high)
    breakpoints = [
        (0.0, 12.0, 0, 50),       # Good
        (12.1, 35.4, 51, 100),    # Moderate
        (35.5, 55.4, 101, 150),   # Unhealthy for Sensitive Groups
        (55.5, 150.4, 151, 200),  # Unhealthy
        (150.5, 250.4, 201, 300), # Very Unhealthy
        (250.5, 350.4, 301, 400), # Hazardous
        (350.5, 500.4, 401, 500), # Hazardous+
    ]

    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= pm25 <= c_high:
            # Linear Interpolation Formula:
            # AQI = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low
            aqi = ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
            return int(round(aqi))

    # Extreme cases
    if pm25 > 500.4:
        return 500
        
    return 0

def get_aqi_category(aqi: int) -> str:
    """Returns the qualitative description of an AQI value."""
    if aqi <= 50: return "Good 🟢"
    if aqi <= 100: return "Moderate 🟡"
    if aqi <= 150: return "Unhealthy for Sensitive Groups 🟠"
    if aqi <= 200: return "Unhealthy 🔴"
    if aqi <= 300: return "Very Unhealthy 🟣"
    return "Hazardous 🟤"
