import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature, EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_IP_ADDRESS
from .hub import IHostHub

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iHost sensors."""
    hub: IHostHub = hass.data[DOMAIN][entry.entry_id]

    async def async_update_data():
        """Fetch data from multiple iHost API endpoints."""
        try:
            runtime = await hub.get_runtime()
            devices = await hub.get_devices()
            security = await hub.get_security()
            return {
                "runtime": runtime,
                "devices": devices,
                "security": security,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="iHost Runtime Data",
        update_method=async_update_data,
        update_interval=timedelta(seconds=60),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        IHostLastBootSensor(coordinator, entry),
        IHostCpuTempSensor(coordinator, entry),
        IHostRamSensor(coordinator, entry),
        IHostDeviceCountSensor(coordinator, entry),
        IHostSecuritySensor(coordinator, entry),
        IHostCpuUsedSensor(coordinator, entry),
        IHostSdCardUsedSensor(coordinator, entry),
        IHostIpAddressSensor(coordinator, entry),
    ])


class IHostBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for iHost."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        
        hub = coordinator.hass.data[DOMAIN][entry.entry_id]
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


class IHostLastBootSensor(IHostBaseSensor):
    """Representation of the iHost Last boot sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "last_boot"
        self._attr_unique_id = f"{entry.entry_id}_last_boot"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        runtime = self.coordinator.data.get("runtime", {})
        power_up_time = runtime.get("power_up_time")
        if power_up_time:
            return dt_util.parse_datetime(power_up_time)
        return None

class IHostCpuTempSensor(IHostBaseSensor):
    """Representation of the iHost CPU Temperature."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "cpu_temperature"
        self._attr_unique_id = f"{entry.entry_id}_cpu_temp"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        runtime = self.coordinator.data.get("runtime", {})
        # L'unité peut être en °C ou °F, mais par défaut on reçoit "c"
        return runtime.get("cpu_temp")

class IHostRamSensor(IHostBaseSensor):
    """Representation of the iHost RAM usage."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "ram_usage"
        self._attr_unique_id = f"{entry.entry_id}_ram_usage"
        self._attr_icon = "mdi:memory"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        runtime = self.coordinator.data.get("runtime", {})
        return runtime.get("ram_used")

class IHostDeviceCountSensor(IHostBaseSensor):
    """Representation of the iHost Device count."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "devices_count"
        self._attr_unique_id = f"{entry.entry_id}_device_count"
        self._attr_icon = "mdi:devices"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        devices = self.coordinator.data.get("devices", [])
        return len(devices)

class IHostSecuritySensor(IHostBaseSensor):
    """Representation of the iHost Security Mode."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "security_mode"
        self._attr_unique_id = f"{entry.entry_id}_security_mode"
        self._attr_icon = "mdi:shield-home"

    @property
    def native_value(self):
        security_list = self.coordinator.data.get("security", [])
        # Parcourt la liste des modes de sécurité pour trouver celui actif
        for mode in security_list:
            if mode.get("enable") is True:
                return mode.get("name")
        return "Disarmed"

class IHostCpuUsedSensor(IHostBaseSensor):
    """Representation of the iHost CPU usage."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "cpu_usage"
        self._attr_unique_id = f"{entry.entry_id}_cpu_usage"
        self._attr_icon = "mdi:cpu-64-bit"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        runtime = self.coordinator.data.get("runtime", {})
        return runtime.get("cpu_used")

class IHostSdCardUsedSensor(IHostBaseSensor):
    """Representation of the iHost SD Card usage."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "sd_card_usage"
        self._attr_unique_id = f"{entry.entry_id}_sd_card_usage"
        self._attr_icon = "mdi:sd"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        runtime = self.coordinator.data.get("runtime", {})
        return runtime.get("sd_card_used")

class IHostIpAddressSensor(IHostBaseSensor):
    """Representation of the iHost IP Address."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "ip_address"
        self._attr_unique_id = f"{entry.entry_id}_ip_address"
        self._attr_icon = "mdi:ip-network"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._ip_address = entry.data.get(CONF_IP_ADDRESS)

    @property
    def native_value(self):
        return self._ip_address
