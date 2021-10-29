"""Sensor platform for Duke Energy Gateway."""
import logging
from typing import Any, Awaitable
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
)
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.util import dt
from pyduke_energy.types import (
    GatewayStatus,
    MeterInfo,
    RealtimeUsageMeasurement,
    UsageMeasurement,
)

from .const import DOMAIN
from .coordinator import DukeEnergyGatewayUsageDataUpdateCoordinator
from .entity import DukeEnergyGatewayEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


class _Sensor:
    def __init__(
        self,
        entity_id: str,
        name: str,
        unit: str,
        icon: str,
        device_class: str,
        state_class: str,
    ):
        self.entity_id = entity_id
        self.name = name
        self.unit = unit
        self.icon = icon
        self.device_class = device_class
        self.state_class = state_class

    @property
    def should_poll(self) -> bool:
        """Whether or not to poll."""
        return True

    def state(self, _coordinator: DukeEnergyGatewayUsageDataUpdateCoordinator) -> Any:
        """Override to define the state function."""

    def extra_state_attrs(
        self,
        _coordinator: DukeEnergyGatewayUsageDataUpdateCoordinator,
        attrs: dict[str, str],
    ) -> dict[str, str]:
        """Override to return any extra state attributes desired."""
        return attrs


class _PollSensor(_Sensor):
    @property
    def should_poll(self) -> bool:
        return True


class _PushSensor(_Sensor):
    @property
    def should_poll(self) -> bool:
        return False

    async def async_subscribe(
        self, coordinator: DukeEnergyGatewayUsageDataUpdateCoordinator
    ) -> Awaitable[None]:
        """Use to setup a subscription to the push event producer."""


class _TotalUsageTodaySensor(_PollSensor):
    def __init__(self):
        super().__init__(
            "usage_today_kwh",
            "Usage Today [kWh]",
            "kWh",
            "mdi:flash",
            "energy",
            STATE_CLASS_TOTAL_INCREASING,
        )

    def state(self, coordinator: DukeEnergyGatewayUsageDataUpdateCoordinator):
        """Return today's usage by summing all measurements."""
        gw_usage: list[UsageMeasurement] = coordinator.data
        if gw_usage and len(gw_usage) > 0:
            today_usage = sum(x.usage for x in gw_usage) / 1000
        else:
            today_usage = 0
        return today_usage

    def extra_state_attrs(
        self,
        coordinator: DukeEnergyGatewayUsageDataUpdateCoordinator,
        attrs: dict[str, str],
    ):
        """Record the timestamp of the last measurement."""
        gw_usage: list[UsageMeasurement] = coordinator.data
        if gw_usage and len(gw_usage) > 0:
            last_measurement = dt.as_local(
                dt.utc_from_timestamp(gw_usage[-1].timestamp)
            )
        else:
            # If no data then it's probably the start of the day so use that as the dates
            last_measurement = dt.start_of_local_day()
        attrs["last_measurement"] = last_measurement
        return attrs


class _RealtimeUsageSensor(_PushSensor):
    def __init__(self):
        super().__init__(
            "current_usage_kw",
            "Current Usage [kW]",
            "kW",
            "mdi:flash",
            "power",
            STATE_CLASS_MEASUREMENT,
        )

    @staticmethod
    def on_new_measurement(measurement: RealtimeUsageMeasurement):
        """Handle a new measurement from the real-time stream."""
        _LOGGER.debug("New measurement received: %f", measurement.usage)

    def connect_to_dispatcher(
        self, coordinator: DukeEnergyGatewayUsageDataUpdateCoordinator
    ) -> None:
        """Subscribe to the real-time data stream."""
        coordinator.realtime_connect_to_dispatcher(
            _RealtimeUsageSensor.on_new_measurement
        )


SENSORS = [_TotalUsageTodaySensor(), _RealtimeUsageSensor()]


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]

    coordinator = data["coordinator"]
    if not coordinator:
        return False

    meter = data["meter"]
    if not meter:
        return False

    gateway = data["gateway"]
    if not gateway:
        return False

    # Prior to v1.0, the gateway device had the entity ID in its unique identifier.
    # This causes issues when we started adding multiple entities (creates multiple devices).
    # To fix this, we will check if the old device exists and update its identifier.
    registry = async_get_device_registry(hass)
    device_to_update = registry.async_get_device(
        identifiers={(DOMAIN, "duke_energy_usage_today_kwh")}, connections=set()
    )
    if device_to_update:
        _LOGGER.info(
            "Correcting Duke Energy Gateway Device %s unique identifier after 1.0 update",
            gateway.id,
        )
        registry.async_update_device(
            device_to_update.id, new_identifiers={(DOMAIN, gateway.id)}
        )

    sensors = []
    for sensor in SENSORS:
        sensors.append(
            DukeEnergyGatewaySensor(coordinator, entry, sensor, meter, gateway)
        )

        # if isinstance(sensor, _PushSensor):
        # sensor.connect_to_dispatcher(coordinator)

    async_add_devices(sensors)


class DukeEnergyGatewaySensor(DukeEnergyGatewayEntity, SensorEntity):
    """duke_energy_gateway Sensor class."""

    def __init__(
        self,
        coordinator,
        entry,
        sensor: _Sensor,
        meter: MeterInfo,
        gateway: GatewayStatus,
    ):
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            entry,
            sensor.entity_id,
            meter,
            gateway,
        )
        self._sensor = sensor
        self._meter = meter

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Duke Energy {self._sensor.name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._sensor.state(self.coordinator)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor.unit

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._sensor.icon

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._sensor.device_class

    @property
    def state_class(self):
        """Return the state class of the sensor"""
        return self._sensor.state_class

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        attrs = self._sensor.extra_state_attrs(self.coordinator, attrs)
        return attrs

    @property
    def should_poll(self) -> bool:
        return self._sensor.should_poll
