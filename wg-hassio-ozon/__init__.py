"""The Ozon component."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import load_platform

from .const import DOMAIN
from .ozon_api import OzonAPI
from .storage import OzonStorage

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("username"): cv.string,
                vol.Required("password"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Ozon component."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    
    # Initialize API client
    api = OzonAPI(
        username=conf["username"],
        password=conf["password"],
    )
    
    # Initialize storage
    storage = OzonStorage(hass, "default")
    
    # Store in hass.data
    hass.data[DOMAIN] = {
        "api": api,
        "storage": storage,
    }

    # Load sensor platform
    load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)

    return True

