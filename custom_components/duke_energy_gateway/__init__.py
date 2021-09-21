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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt
from pyduke_energy.client import DukeEnergyClient

from .const import CONF_EMAIL
from .const import CONF_PASSWORD
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    email = entry.data.get(CONF_EMAIL)
    password = entry.data.get(CONF_PASSWORD)

    session = async_get_clientsession(hass)
    client = DukeEnergyClient(email, password, session)
    _LOGGER.debug("Setup Duke Energy API client")

    # Try to find the meter that is used for the gateway
    selected_meter, selected_gateway = await find_meter_with_gateway(client)

    # If no meter was found, we raise an error
    if not selected_meter or not selected_gateway:
        _LOGGER.error(
            "Could not identify a smart meter on your account with gateway access."
        )
        return False

    coordinator = DukeEnergyGatewayUsageDataUpdateCoordinator(hass, client=client)
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

    entry.add_update_listener(async_reload_entry)
    return True


async def find_meter_with_gateway(client: DukeEnergyClient):
    """Find the meter that is used for the gateway by iterating through the accounts and meters."""
    account_list = await client.get_account_list()
    account_numbers_text = ",".join([f"'{a.src_acct_id}'" for a in account_list])
    _LOGGER.debug(
        f"Accounts to check for gateway ({len(account_list)}): {account_numbers_text}"
    )
    for account in account_list:
        try:
            _LOGGER.debug(f"Checking account '{account.src_acct_id}' for gateway")
            account_details = await client.get_account_details(account)
            serial_numbers_text = ",".join(
                [f"'{m.serial_num}'" for m in account_details.meter_infos]
            )
            _LOGGER.debug(
                f"Meters to check for gateway ({len(account_details.meter_infos)}): {serial_numbers_text}"
            )
            for meter in account_details.meter_infos:
                try:
                    _LOGGER.debug(
                        f"Checking meter '{meter.serial_num}' for gateway [meter_type={meter.meter_type}, is_certified_smart_meter={meter.is_certified_smart_meter}]"
                    )
                    if (
                        meter.serial_num
                        and meter.meter_type.upper()  # sometimes blank meters show up
                        == "ELECTRIC"
                        and meter.is_certified_smart_meter
                    ):
                        client.select_meter(meter)
                        gw_status = await client.get_gateway_status()
                        if gw_status is not None:
                            _LOGGER.debug(
                                f"Found meter '{meter.serial_num}' with gateway '{gw_status.id}'"
                            )
                            return meter, gw_status
                        else:
                            _LOGGER.debug(
                                f"No gateway status for meter '{meter.serial_num}'"
                            )
                except Exception as e:
                    # Try the next meter if anything fails above
                    _LOGGER.debug(
                        f"Failed to check meter '{meter.serial_num}' on account '{account.src_acct_id}': {e}"
                    )
                    pass
        except Exception as e:
            # Try the next account if anything fails above
            _LOGGER.debug(
                f"Failed to find meter on account '{account.src_acct_id}': {e}"
            )
            pass
    return None, None


class DukeEnergyGatewayUsageDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching usage data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DukeEnergyClient,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library to get last day of minute-by-minute usage data."""
        try:
            today_start = dt.start_of_local_day()
            today_end = today_start + timedelta(days=1)
            return await self.api.get_gateway_usage(today_start, today_end)
        except Exception as exception:
            raise UpdateFailed(
                f"Error communicating with Duke Energy Usage API: {exception}"
            ) from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
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

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
