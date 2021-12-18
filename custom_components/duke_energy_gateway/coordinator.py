"""Data update coordinator for Duke Energy Gateway entities."""
import asyncio
import logging
from asyncio.tasks import Task
from datetime import datetime
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
        realtime_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.client = client
        self.realtime = realtime
        self.realtime_interval = realtime_interval
        self.realtime_next_send = datetime.utcnow()
        self.realtime_task: Task = None
        self.async_realtime_remove_subscriber_funcs_by_source: dict[
            str, Callable[[], None]
        ] = {}
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
            self.realtime.on_message = self._realtime_on_message
            self.realtime_task = asyncio.create_task(
                self.realtime.connect_and_subscribe_forever()
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

    def _realtime_on_message(self, msg):
        """Handler for the real-time usage MQTT messages."""
        try:
            measurement = self.realtime.msg_to_usage_measurement(msg)
        except (ValueError, TypeError) as exception:
            _LOGGER.error(
                "Error while parsing real-time usage message: %s [Message='%s']",
                exception,
                msg.payload.decode("utf8"),
            )
            return

        if measurement:
            # Throttle sending calls to reduce amount of data bneing produced.
            should_send = (
                self.realtime_interval is None
                or self.realtime_next_send is None
                or datetime.utcnow() >= self.realtime_next_send
            )
            if should_send:
                self.realtime_next_send = datetime.utcnow() + self.realtime_interval
                dispatcher_send(self.hass, REALTIME_DISPATCH_SIGNAL, measurement)
            else:
                _LOGGER.debug(
                    "Ignoring real-time update as still in throttling interval"
                )

    def async_realtime_subscribe_to_dispatcher(
        self, source: str, target: Callable[[RealtimeUsageMeasurement], Any]
    ):
        """Setup a subscriber to receive new real-time measurements."""
        # If this source is already subscribed, re-use the existing one
        if source in self.async_realtime_remove_subscriber_funcs_by_source:
            _LOGGER.warning(
                "Attempting to subscribe to dispatcher by source that is already subscribed: %s",
                source,
            )
            return

        # Connect function returns a function that removes the subscription. Save for later.
        self.async_realtime_remove_subscriber_funcs_by_source[
            source
        ] = async_dispatcher_connect(self.hass, REALTIME_DISPATCH_SIGNAL, target)
        _LOGGER.debug("Subscribed target for %s to dispatcher", source)

    def async_realtime_unsubscribe_from_dispatcher(self, source: str):
        """Remove a subscriber from the dispatch."""
        if source in self.async_realtime_remove_subscriber_funcs_by_source:
            _LOGGER.debug("Removing subscribers to dispatcher for %s", source)
            self.async_realtime_remove_subscriber_funcs_by_source[source]()
            self.async_realtime_remove_subscriber_funcs_by_source.pop(source)

    def async_realtime_unsubscribe_all_from_dispatcher(self):
        """Remove all subscribers from the dispatch."""
        sources = self.async_realtime_remove_subscriber_funcs_by_source.keys()
        for source in sources:
            self.async_realtime_unsubscribe_from_dispatcher(source)
