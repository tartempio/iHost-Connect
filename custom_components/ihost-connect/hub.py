import logging
from typing import Any
import aiohttp

_LOGGER = logging.getLogger(__name__)

class CannotConnect(Exception):
    """Error to indicate we cannot connect."""

class ButtonNotPressed(Exception):
    """Error to indicate the link button was not pressed."""

class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""

class IHostHub:
    """Hub to interact with iHost."""

    def __init__(self, ip_address: str, token: str | None = None) -> None:
        """Initialize."""
        self.ip_address = ip_address
        self.token = token
        self.base_url = f"http://{self.ip_address}/open-api/v2/rest/bridge"

    async def get_access_token(self) -> str:
        """Fetch the token."""
        url = f"{self.base_url}/access_token"
        headers = {"Content-Type": "application/json"}
        # According to doc, it's a GET request but might need app_name.
        # We pass it via json body just in case the API expects it there due to Content-Type: application/json
        payload = {"app_name": "HomeAssistant"}
        
        try:
            _LOGGER.debug("Sending GET request to %s with headers: %s and payload: %s", url, headers, payload)
            async with aiohttp.ClientSession() as session:
                # Passer le app_name en paramètre d'URL (query string) car pour une requête GET, le body est souvent ignoré.
                response = await session.get(url, headers=headers, params=payload)
                _LOGGER.debug("Received HTTP status %s from iHost", response.status)
                
                if response.status != 200:
                    _LOGGER.error("Failed to connect. HTTP Status: %s. Response content: %s", response.status, await response.text())
                    raise CannotConnect
                
                result = await response.json()
                _LOGGER.debug("iHost response payload: %s", result)
                
                if result.get("error") == 401:
                    raise ButtonNotPressed
                if result.get("error") != 0:
                    _LOGGER.error("API Error: %s", result)
                    raise CannotConnect
                
                data = result.get("data", {})
                self.token = data.get("token")
                return self.token
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error: %s", err)
            raise CannotConnect

    async def get_runtime(self) -> dict[str, Any]:
        """Fetch runtime payload."""
        if not self.token:
            raise InvalidAuth

        url = f"{self.base_url}/runtime"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            _LOGGER.debug("Sending GET request to %s with headers: %s", url, headers)
            async with aiohttp.ClientSession() as session:
                response = await session.get(url, headers=headers)
                _LOGGER.debug("Received HTTP status %s from iHost", response.status)

                if response.status != 200:
                    _LOGGER.error("Failed to connect. HTTP Status: %s. Response content: %s", response.status, await response.text())
                    raise CannotConnect
                
                result = await response.json()
                _LOGGER.debug("iHost runtime response: %s", result)

                if result.get("error") in (401, 403):
                    raise InvalidAuth
                if result.get("error") != 0:
                    _LOGGER.error("API Error during runtime fetch: %s", result)
                    raise CannotConnect
                
                return result.get("data", {})
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during runtime fetch: %s", err)
            raise CannotConnect

    async def get_devices(self) -> list[dict[str, Any]]:
        """Fetch list of connected devices."""
        if not self.token:
            raise InvalidAuth
        
        url = f"{self.base_url.replace('/bridge', '/devices')}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url, headers=headers)
                if response.status != 200:
                    return []
                result = await response.json()
                data = result.get("data", {})
                return data.get("device_list", [])
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during devices fetch: %s", err)
            return []

    async def get_security(self) -> list[dict[str, Any]]:
        """Fetch security status."""
        if not self.token:
            raise InvalidAuth
        
        url = f"{self.base_url.replace('/bridge', '/security')}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url, headers=headers)
                if response.status != 200:
                    return []
                result = await response.json()
                data = result.get("data", {})
                return data.get("security_list", [])
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during security fetch: %s", err)
            return []

    async def reboot(self) -> None:
        """Trigger a gateway reboot."""
        if not self.token:
            raise InvalidAuth
        
        url = "http://" + self.ip_address + "/open-api/v2/rest/hardware/reboot"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(url, headers=headers)
                _LOGGER.debug("Reboot command sent successfully")
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during reboot: %s", err)

    async def get_bridge_info(self) -> dict[str, Any]:
        """Fetch gateway info."""
        if not self.token:
            raise InvalidAuth

        url = f"{self.base_url}"
        headers = {
            "Content-Type": "application/json",
            # Document says no auth for /bridge, but sometimes it's better to pass if we have it or standard.
            # But doc says "Conditions: None" and does not list auth for this specific one, though other ones do.
        }
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url, headers=headers)
                if response.status != 200:
                    _LOGGER.error("Failed to fetch bridge info. Status: %s", response.status)
                    raise CannotConnect
                
                result = await response.json()
                return result.get("data", {})
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during bridge info fetch: %s", err)
            raise CannotConnect
