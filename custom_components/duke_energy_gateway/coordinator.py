"""Data update coordinator for Duke Energy Gateway entities."""
import asyncio
import logging
from datetime import timedelta
from typing import Any
from typing import Callable

from homeassistant.core import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
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
        self.realtime_task = None
        self.async_remove_subscriber_funcs_by_source = {}

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
            self.realtime_task = asyncio.create_task(
                self.realtime.connect_and_subscribe()
            )
            _LOGGER.debug("Triggered real-time connect/subscribe async task")
        except Exception as exception:
            _LOGGER.error(
                "Failure trying to connect and subscribe to real-time usage: %s",
                exception,
            )
            raise

    def realtime_cancel(self):
        """Cancel the real-time usage MQTT stream, which will unsubscribe."""
        if self.realtime_task:
            self.realtime_task.cancel()
            self.realtime_task = None
            _LOGGER.debug("Cancelled real-time async task")

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

    def async_realtime_subscribe_to_dispatcher(
        self, source: str, target: Callable[[RealtimeUsageMeasurement], Any]
    ):
        """Setup a subscriber to receive new real-time measurements."""
        remove_subscriber = async_dispatcher_connect(
            self.hass, REALTIME_DISPATCH_SIGNAL, target
        )
        _LOGGER.debug("Subscribed target for %s to dispatcher", source)
        self.async_remove_subscriber_funcs_by_source[source] = remove_subscriber

    def async_realtime_unsubscribe_from_dispatcher(self, source: str):
        """Remove a subscriber from the dispatch."""
        if source in self.async_remove_subscriber_funcs_by_source:
            _LOGGER.debug("Removing subscribers to dispatcher for %s", source)
            self.async_remove_subscriber_funcs_by_source[source]()
            self.async_remove_subscriber_funcs_by_source[source] = None
