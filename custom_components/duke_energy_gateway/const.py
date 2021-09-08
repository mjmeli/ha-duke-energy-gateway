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

# Defaults
DEFAULT_NAME = DOMAIN

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
