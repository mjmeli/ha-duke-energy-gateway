"""Sensor platform for Duke Energy Gateway."""
from dataclasses import dataclass
import logging
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
)
from homeassistant.helpers import device_registry
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


@dataclass
class _SensorMetadata:
    entity_id: str
    name: str
    unit: str
    icon: str
    device_class: str
    state_class: str


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
    registry = device_registry.async_get(hass)
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

    # Total usage today sensor
    total_usage_today_sensor_metadata = _SensorMetadata(
        "usage_today_kwh",
        "Usage Today [kWh]",
        "kWh",
        "mdi:flash",
        "energy",
        STATE_CLASS_TOTAL_INCREASING,
    )
    sensors.append(
        _TotalUsageTodaySensor(
            coordinator, entry, total_usage_today_sensor_metadata, meter, gateway
        )
    )

    # Real-time usage sensor
    current_usage_sensor_metadata = _SensorMetadata(
        "current_usage_kw",
        "Current Usage [kW]",
        "kW",
        "mdi:flash",
        "power",
        STATE_CLASS_MEASUREMENT,
    )
    sensors.append(
        _RealtimeUsageSensor(
            coordinator, entry, current_usage_sensor_metadata, meter, gateway
        )
    )
    # sensor.connect_to_dispatcher(coordinator)

    async_add_devices(sensors)


class DukeEnergyGatewaySensor(DukeEnergyGatewayEntity, SensorEntity):
    """duke_energy_gateway Sensor class."""

    def __init__(
        self,
        coordinator,
        entry,
        sensor_metadata: _SensorMetadata,
        meter: MeterInfo,
        gateway: GatewayStatus,
    ):
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            entry,
            sensor_metadata.entity_id,
            meter,
            gateway,
        )
        self._sensor_metadata = sensor_metadata
        self._meter = meter

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Duke Energy {self._sensor_metadata.name}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor_metadata.unit

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._sensor_metadata.icon

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._sensor_metadata.device_class

    @property
    def state_class(self):
        """Return the state class of the sensor"""
        return self._sensor_metadata.state_class


class _TotalUsageTodaySensor(DukeEnergyGatewaySensor):
    @property
    def state(self):
        """Return today's usage by summing all measurements."""
        gw_usage: list[UsageMeasurement] = self.coordinator.data
        if gw_usage and len(gw_usage) > 0:
            today_usage = sum(x.usage for x in gw_usage) / 1000
        else:
            today_usage = 0
        return today_usage

    @property
    def extra_state_attributes(self):
        """Record the timestamp of the last measurement into state attributes."""
        attrs = super().extra_state_attributes

        gw_usage: list[UsageMeasurement] = self.coordinator.data
        if gw_usage and len(gw_usage) > 0:
            last_measurement = dt.as_local(
                dt.utc_from_timestamp(gw_usage[-1].timestamp)
            )
        else:
            # If no data then it's probably the start of the day so use that as the dates
            last_measurement = dt.start_of_local_day()
        attrs["last_measurement"] = last_measurement

        return attrs


class _RealtimeUsageSensor(DukeEnergyGatewaySensor):
    @property
    def should_poll(self) -> bool:
        return False

    @staticmethod
    def on_new_measurement(measurement: RealtimeUsageMeasurement):
        """Handle a new measurement from the real-time stream."""
        _LOGGER.debug("New measurement received: %f", measurement.usage)

    def connect_to_dispatcher(self) -> None:
        """Subscribe to the real-time data stream."""
        self.coordinator.realtime_connect_to_dispatcher(
            _RealtimeUsageSensor.on_new_measurement
        )
