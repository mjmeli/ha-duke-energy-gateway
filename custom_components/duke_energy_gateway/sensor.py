"""Sensor platform for Duke Energy Gateway."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING
from homeassistant.util import dt
from pyduke_energy.types import GatewayStatus
from pyduke_energy.types import MeterInfo
from pyduke_energy.types import UsageMeasurement

from .const import DOMAIN
from .entity import DukeEnergyGatewayEntity


class _Sensor:
    def __init__(self, entity_id, name, unit, icon, device_class):
        self.entity_id = entity_id
        self.name = name
        self.unit = unit
        self.icon = icon
        self.device_class = device_class


# Sensor are defined like: Name, Unit, icon, device class
SENSORS = [
    _Sensor("usage_today_kwh", "Usage Today [kWh]", "kWh", "mdi:flash", "energy")
]


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

    sensors = []
    for sensor in SENSORS:
        sensors.append(
            DukeEnergyGatewaySensor(coordinator, entry, sensor, meter, gateway)
        )

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
        # Currently there is only one sensor so this works. If we add more then we will need to handle this better.
        gw_usage: list[UsageMeasurement] = self.coordinator.data
        if gw_usage and len(gw_usage) > 0:
            today_usage = sum(x.usage for x in gw_usage) / 1000
        else:
            today_usage = 0
        return today_usage

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
        return STATE_CLASS_TOTAL_INCREASING

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = super().extra_state_attributes

        # Currently there is only one sensor so this works. If we add more then we will need to handle this better.
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
