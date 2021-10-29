"""DukeEnergyGatewayEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyduke_energy.types import GatewayStatus
from pyduke_energy.types import MeterInfo

from .const import ATTRIBUTION
from .const import DOMAIN
from .const import NAME
from .const import VERSION
from .coordinator import DukeEnergyGatewayUsageDataUpdateCoordinator


class DukeEnergyGatewayEntity(CoordinatorEntity):
    def __init__(
        self,
        coordinator: DukeEnergyGatewayUsageDataUpdateCoordinator,
        config_entry,
        entity_id: str,
        meter: MeterInfo,
        gateway: GatewayStatus,
    ):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._config_entry = config_entry
        self._entity_id = entity_id
        self._meter = meter
        self._gateway = gateway

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"duke_energy_{self._entity_id}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._gateway.id)},
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
