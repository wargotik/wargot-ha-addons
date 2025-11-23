"""Storage for Ozon integration."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)


class OzonStorage:
    """Handle storage for Ozon integration."""

    def __init__(self, hass, entry_id: str) -> None:
        """Initialize storage."""
        self.hass = hass
        self.entry_id = entry_id
        self.store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry_id}")

    async def async_load(self) -> dict[str, Any]:
        """Load data from storage."""
        try:
            data = await self.store.async_load()
            if data:
                return data
            return {"favorites": []}
        except Exception as err:
            _LOGGER.error("Error loading storage: %s", err)
            return {"favorites": []}

    async def async_save(self, data: dict[str, Any]) -> None:
        """Save data to storage."""
        try:
            await self.store.async_save(data)
        except Exception as err:
            _LOGGER.error("Error saving storage: %s", err)

    async def async_save_favorites(self, favorites: list[dict[str, Any]]) -> None:
        """Save favorites to storage."""
        data = await self.async_load()
        data["favorites"] = favorites
        await self.async_save(data)

    async def async_get_favorites(self) -> list[dict[str, Any]]:
        """Get favorites from storage."""
        data = await self.async_load()
        return data.get("favorites", [])

