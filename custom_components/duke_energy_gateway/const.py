"""Constants for Duke Energy Gateway."""
# Base component constants
NAME = "Duke Energy Gateway"
DOMAIN = "duke_energy_gateway"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.0.0"

ATTRIBUTION = "Data provided by Duke Energy Unofficial API"
ISSUE_URL = "https://github.com/mjmeli/ha-duke-energy-gateway/issues"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_REALTIME_INTERVAL = "realtimeInterval"
CONF_REALTIME_INTERVAL_DEFAULT_SEC = 0  # no throttling

# Defaults
DEFAULT_NAME = DOMAIN

REALTIME_DISPATCH_SIGNAL = f"{DOMAIN}_realtime_dispatch_signal"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
