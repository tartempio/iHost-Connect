import logging
from datetime import timedelta

import aiohttp
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

GITHUB_LATEST_RELEASE_URL = "https://api.github.com/repos/eWeLinkCUBE/CUBE-OS/releases/latest"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iHost binary sensors."""
    hub = hass.data[DOMAIN][entry.entry_id]

    async def async_update_data():
        """Fetch latest release from GitHub."""
        try:
            session = async_get_clientsession(hass)
            async with session.get(GITHUB_LATEST_RELEASE_URL) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching from GitHub: {response.status}")
                data = await response.json()
                return data.get("tag_name", "").lstrip("v")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error to GitHub: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="iHost Firmware Update",
        update_method=async_update_data,
        update_interval=timedelta(hours=6),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([IHostFirmwareUpdateBinarySensor(coordinator, entry)])


class IHostFirmwareUpdateBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for firmware update availability."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_name = "Firmware Update"
        self._attr_unique_id = f"{entry.entry_id}_firmware_update"
        self._attr_device_class = BinarySensorDeviceClass.UPDATE
        
        hub = coordinator.hass.data[DOMAIN][entry.entry_id]
        info = getattr(hub, 'bridge_info', {})
        self._current_version = info.get("fw_version")
        
        device_name = info.get("name", "iHost")
        mac_addr = info.get("mac")

        dev_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "SONOFF",
            "model": "eWeLink CUBE",
        }
        if self._current_version:
            dev_info["sw_version"] = self._current_version
        if mac_addr:
            from homeassistant.helpers import device_registry as dr
            dev_info["connections"] = {(dr.CONNECTION_NETWORK_MAC, mac_addr)}

        self._attr_device_info = dev_info

    @property
    def is_on(self) -> bool | None:
        """Return true if an update is available."""
        latest_version = self.coordinator.data
        if not self._current_version or not latest_version:
            return None
            
        return self._current_version != latest_version

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "current_version": self._current_version,
            "latest_version": self.coordinator.data,
        }
