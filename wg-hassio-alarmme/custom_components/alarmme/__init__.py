"""AlarmMe integration for Home Assistant."""
from __future__ import annotations

import logging
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "alarmme"
ADDON_SLUG = "wg-hassio-alarmme"


async def _check_addon_available(hass: HomeAssistant) -> bool:
    """Check if AlarmMe add-on is available."""
    try:
        # Try to check via Supervisor API
        supervisor_url = "http://supervisor"
        
        async with aiohttp.ClientSession() as session:
            # Check if add-on is installed and running
            try:
                async with session.get(
                    f"{supervisor_url}/addons/{ADDON_SLUG}/info",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("data", {}).get("state") == "started":
                            _LOGGER.info("AlarmMe add-on is running")
                            return True
                        else:
                            _LOGGER.warning(
                                "AlarmMe add-on is installed but not running. "
                                "State: %s. Please start the add-on for full functionality.",
                                data.get("data", {}).get("state", "unknown")
                            )
                            return False
            except aiohttp.ClientError:
                # Supervisor API not available, try health endpoint
                pass
            
            # Fallback: try to check add-on health endpoint via ingress
            try:
                # Try to access add-on via ingress (if available)
                async with session.get(
                    f"http://supervisor/core/api/hassio_ingress/{ADDON_SLUG}/health",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    if resp.status == 200:
                        _LOGGER.info("AlarmMe add-on is accessible")
                        return True
            except aiohttp.ClientError:
                pass
            
            # If we can't check, log warning but don't block
            _LOGGER.warning(
                "Could not verify AlarmMe add-on status. "
                "Please ensure the add-on is installed and running for full functionality."
            )
            return False
            
    except Exception as err:
        _LOGGER.warning(
            "Error checking AlarmMe add-on availability: %s. "
            "Integration will continue to load, but add-on functionality may be limited.",
            err
        )
        return False


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up AlarmMe integration."""
    # Check if add-on is available
    addon_available = await _check_addon_available(hass)
    
    if not addon_available:
        _LOGGER.warning(
            "AlarmMe add-on may not be available. "
            "Switches will be created, but the add-on may not be able to monitor their state. "
            "Please install and start the AlarmMe add-on for full functionality."
        )
    
    # Import switch platform
    await hass.helpers.discovery.async_load_platform("switch", DOMAIN, {}, config)
    return True

