"""
Custom integration to integrate Duke Energy Gateway with Home Assistant.

For more details about this integration, please refer to
https://github.com/mjmeli/ha-duke-energy-gateway
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pyduke_energy.client import DukeEnergyClient
from pyduke_energy.realtime import DukeEnergyRealtime

from .const import CONF_EMAIL
from .const import CONF_PASSWORD
from .const import CONF_REALTIME_INTERVAL
from .const import CONF_REALTIME_INTERVAL_DEFAULT_SEC
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE
from .coordinator import DukeEnergyGatewayUsageDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(_hass: HomeAssistant, _config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    email = entry.data.get(CONF_EMAIL)
    password = entry.data.get(CONF_PASSWORD)
    realtime_interval = entry.options.get(
        CONF_REALTIME_INTERVAL, CONF_REALTIME_INTERVAL_DEFAULT_SEC
    )

    session = async_get_clientsession(hass)
    client = DukeEnergyClient(email, password, session)
    realtime = DukeEnergyRealtime(client)
    _LOGGER.debug("Set up Duke Energy API clients")

    # Find the meter that is used for the gateway
    selected_meter, selected_gateway = await client.select_default_meter()

    # If no meter was found, we raise an error
    if not selected_meter:
        _LOGGER.error(
            "Could not identify a smart meter on your account with gateway access."
        )
        return False

    coordinator = DukeEnergyGatewayUsageDataUpdateCoordinator(
        hass,
        client=client,
        realtime=realtime,
        realtime_interval=timedelta(seconds=realtime_interval),
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "meter": selected_meter,
        "gateway": selected_gateway,
    }

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator: DukeEnergyGatewayUsageDataUpdateCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]["coordinator"]

    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    # Cleanup real-time stream if it wasn't already done so (it should be done by the sensor entity)
    _LOGGER.debug("Checking for clean-up of real-time stream in async_unload_entry")
    coordinator.realtime_cancel()
    coordinator.async_realtime_unsubscribe_all_from_dispatcher()

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
