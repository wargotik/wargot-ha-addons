"""AlarmMe integration for Home Assistant."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "alarmme"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up AlarmMe integration."""
    # Import switch platform
    await hass.helpers.discovery.async_load_platform("switch", DOMAIN, {}, config)
    return True

