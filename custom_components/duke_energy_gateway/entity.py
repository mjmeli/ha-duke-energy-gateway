"""DukeEnergyGatewayEntity class"""
from pyduke_energy.types import MeterInfo, GatewayStatus

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt

from .const import ATTRIBUTION
from .const import DOMAIN
from .const import NAME
from .const import VERSION


class DukeEnergyGatewayEntity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry, entity_id, meter, gateway):
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._entity_id = entity_id
        self._meter = entity_id
        self._gateway = gateway

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"duke_energy_{self._entity_id}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": f"{NAME} {self._gateway.id}",
            "model": VERSION,
            "manufacturer": NAME,
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "integration": DOMAIN,
            "meter": self._meter.serial_num,
            "gateway": self._gateway.id,
        }
