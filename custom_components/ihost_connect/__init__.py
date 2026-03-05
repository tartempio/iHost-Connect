import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_TOKEN
from .hub import IHostHub, CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON, Platform.BINARY_SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iHost from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    hub = IHostHub(
        ip_address=entry.data[CONF_IP_ADDRESS],
        token=entry.data[CONF_TOKEN],
    )

    try:
        # Verify connection by getting the runtime payload
        await hub.get_runtime()
        # Fetch bridge info to get mac, fw_version, and device name
        hub.bridge_info = await hub.get_bridge_info()
    except InvalidAuth:
        _LOGGER.error("Invalid token to connect to iHost")
        return False
    except CannotConnect:
        _LOGGER.error("Cannot connect to iHost")
        return False

    hass.data[DOMAIN][entry.entry_id] = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
