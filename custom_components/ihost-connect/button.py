import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iHost buttons."""
    # S'il a été enregistré en tant que dictionnaire ou hub, on récupère le hub.
    hub = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        IHostRebootButton(hub, entry),
    ])


class IHostBaseButton(ButtonEntity):
    """Representation of an iHost base button."""

    def __init__(self, hub, entry: ConfigEntry) -> None:
        """Initialize the button."""
        self.hub = hub
        self._attr_has_entity_name = True
        
        info = hub.bridge_info if hasattr(hub, 'bridge_info') else {}
        device_name = info.get("name", "iHost")
        fw_version = info.get("fw_version")
        mac_addr = info.get("mac")

        dev_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "SONOFF",
            "model": "eWeLink CUBE",
        }
        if fw_version:
            dev_info["sw_version"] = fw_version
        if mac_addr:
            from homeassistant.helpers import device_registry as dr
            dev_info["connections"] = {(dr.CONNECTION_NETWORK_MAC, mac_addr)}

        self._attr_device_info = dev_info


class IHostRebootButton(IHostBaseButton):
    """Representation of an iHost reboot button."""

    def __init__(self, hub, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(hub, entry)
        self._attr_name = "Reboot"
        self._attr_unique_id = f"{entry.entry_id}_reboot"
        self._attr_icon = "mdi:restart"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Reboot requested for iHost.")
        await self.hub.reboot()
