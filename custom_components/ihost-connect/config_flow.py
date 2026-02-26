import logging
from typing import Any
import asyncio

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_TOKEN
from .hub import IHostHub, CannotConnect, InvalidAuth, ButtonNotPressed

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iHost."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self.ip_address: str = ""

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        self.ip_address = discovery_info.host
        
        # Determine a unique ID from properties or hostname
        mac = discovery_info.properties.get("mac")
        device_id = discovery_info.properties.get("id")
        unique_id = mac or device_id or discovery_info.hostname.removesuffix(".local.")
        
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates={CONF_IP_ADDRESS: self.ip_address})

        # Also abort if a manually-added entry already uses this IP address
        self._async_abort_entries_match({CONF_IP_ADDRESS: self.ip_address})

        self.context.update({"title_placeholders": {"name": discovery_info.hostname.removesuffix(".local.")}})
        
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        if user_input is not None:
            return await self.async_step_link()

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"ip_address": self.ip_address},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self.ip_address = user_input[CONF_IP_ADDRESS]
            self._async_abort_entries_match({CONF_IP_ADDRESS: self.ip_address})
            return await self.async_step_link()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_link(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the link step: user needs to approve the connection on the iHost web interface."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            hub = IHostHub(self.ip_address)
            # Try to get the token for up to 10 seconds (30 retries with 2s wait)
            for _ in range(30):
                try:
                    token = await hub.get_access_token()
                    return self.async_create_entry(
                        title="iHost Connect",
                        data={
                            CONF_IP_ADDRESS: self.ip_address,
                            CONF_TOKEN: token,
                        },
                    )
                except ButtonNotPressed:
                    await asyncio.sleep(2)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                    break
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                    break
            
            if "base" not in errors:
                errors["base"] = "button_not_pressed"

        return self.async_show_form(
            step_id="link",
            errors=errors,
            # No fields required, just a submit button
            data_schema=vol.Schema({}),
            description_placeholders={"ip_address": self.ip_address},
        )
