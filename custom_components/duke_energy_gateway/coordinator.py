"""Data update coordinator for Duke Energy Gateway entities."""
import asyncio
from datetime import timedelta
import logging
from typing import Any, Callable
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.dispatcher import dispatcher_connect, dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt
from pyduke_energy.client import DukeEnergyClient
from pyduke_energy.realtime import DukeEnergyRealtime
from pyduke_energy.types import RealtimeUsageMeasurement

from .const import REALTIME_DISPATCH_SIGNAL

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DukeEnergyGatewayUsageDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching usage data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DukeEnergyClient,
        realtime: DukeEnergyRealtime,
    ) -> None:
        """Initialize."""
        self.client = client
        self.realtime = realtime
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library to get last day of minute-by-minute usage data."""
        try:
            today_start = dt.start_of_local_day()
            today_end = today_start + timedelta(days=1)
            return await self.client.get_gateway_usage(today_start, today_end)
        except Exception as exception:
            raise UpdateFailed(
                f"Error communicating with Duke Energy Usage API: {exception}"
            ) from exception

    def realtime_initialize(self):
        """Setup callbacks, connect, and subscribe to the real-time usage MQTT stream."""
        try:
            self.realtime.on_msg = self._realtime_on_msg
            asyncio.create_task(self.realtime.connect_and_subscribe())
            _LOGGER.debug("Pushed real-time connect/subscribe to async task")
        except Exception as exception:
            _LOGGER.error(
                "Failure trying to connect and subscribe to real-time usage: %s",
                exception,
            )
            raise

    def realtime_connect_to_dispatcher(
        self, target: Callable[[RealtimeUsageMeasurement], Any]
    ):
        """Setup a subscriber to receive new real-time measurements."""
        dispatcher_connect(self.hass, REALTIME_DISPATCH_SIGNAL, target)

    def _realtime_on_msg(self, msg):
        """Handler for the real-time usage MQTT messages."""
        try:
            measurement = self.realtime.msg_to_usage_measurement(msg)
            if measurement:
                dispatcher_send(self.hass, REALTIME_DISPATCH_SIGNAL, measurement)
        except (ValueError, TypeError) as exception:
            _LOGGER.error(
                "Error while parsing real-time usage message: %s [Message='%s']",
                exception,
                msg.payload.decode("utf8"),
            )
