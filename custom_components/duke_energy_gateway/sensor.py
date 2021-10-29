"""Sensor platform for Duke Energy Gateway."""
import logging
from abc import ABC
from abc import abstractstaticmethod
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT
from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING
from homeassistant.helpers import device_registry
from homeassistant.util import dt
from pyduke_energy.types import GatewayStatus
from pyduke_energy.types import MeterInfo
from pyduke_energy.types import RealtimeUsageMeasurement
from pyduke_energy.types import UsageMeasurement

from .const import DOMAIN
from .entity import DukeEnergyGatewayEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


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
    sensors.append(_TotalUsageTodaySensor(coordinator, entry, meter, gateway))

    # Real-time usage sensor
    sensors.append(_RealtimeUsageSensor(coordinator, entry, meter, gateway))
    # sensor.connect_to_dispatcher(coordinator)

    async_add_devices(sensors)


@dataclass
class _SensorMetadata:
    entity_id: str
    name: str
    unit: str
    icon: str
    device_class: str
    state_class: str


class DukeEnergyGatewaySensor(DukeEnergyGatewayEntity, SensorEntity, ABC):
    """duke_energy_gateway Sensor class."""

    def __init__(
        self,
        coordinator,
        entry,
        meter: MeterInfo,
        gateway: GatewayStatus,
    ):
        """Initialize the sensor."""
        self._sensor_metadata = self.get_sensor_metadata()
        super().__init__(
            coordinator,
            entry,
            self._sensor_metadata.entity_id,
            meter,
            gateway,
        )

    @abstractstaticmethod
    def get_sensor_metadata() -> _SensorMetadata:
        """Get the sensor metadata for this sensor. Override in base class."""
        return None

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
    @staticmethod
    def get_sensor_metadata() -> _SensorMetadata:
        return _SensorMetadata(
            "usage_today_kwh",
            "Usage Today [kWh]",
            "kWh",
            "mdi:flash",
            "energy",
            STATE_CLASS_TOTAL_INCREASING,
        )

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
    @staticmethod
    def get_sensor_metadata() -> _SensorMetadata:
        return _SensorMetadata(
            "current_usage_kw",
            "Current Usage [kW]",
            "kW",
            "mdi:flash",
            "power",
            STATE_CLASS_MEASUREMENT,
        )

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
