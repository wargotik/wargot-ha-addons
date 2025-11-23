"""Sensor platform for Ozon component."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=1)  # Update every hour


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict,
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict | None = None,
) -> None:
    """Set up Ozon sensor platform."""
    if DOMAIN not in hass.data:
        return

    data = hass.data[DOMAIN]
    api = data["api"]
    storage = data["storage"]

    coordinator = OzonCoordinator(hass, api, storage)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([OzonFavoritesSensor(coordinator)])


class OzonCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Ozon API."""

    def __init__(self, hass, api, storage):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.storage = storage

    async def _async_update_data(self):
        """Fetch data from Ozon API."""
        try:
            # Get favorites from API
            favorites = await self.api.get_favorites()
            
            # Save to local storage
            await self.storage.async_save_favorites(favorites)
            
            _LOGGER.debug("Fetched %d favorites from Ozon", len(favorites))
            return {"favorites": favorites}
        except Exception as err:
            _LOGGER.error("Error fetching Ozon data: %s", err)
            # On error, try to load from storage
            try:
                favorites = await self.storage.async_get_favorites()
                return {"favorites": favorites}
            except Exception as storage_err:
                _LOGGER.error("Error loading from storage: %s", storage_err)
                raise UpdateFailed(f"Error communicating with API: {err}") from err


class OzonFavoritesSensor(SensorEntity):
    """Representation of Ozon Favorites sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_name = "Ozon Favorites"
        self._attr_unique_id = "ozon_favorites"
        self._attr_icon = "mdi:heart"

    @property
    def native_value(self) -> int:
        """Return the number of favorite items."""
        if self.coordinator.data and "favorites" in self.coordinator.data:
            return len(self.coordinator.data["favorites"])
        return 0

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        if not self.coordinator.data or "favorites" not in self.coordinator.data:
            return {}
        
        favorites = self.coordinator.data["favorites"]
        return {
            "items": [
                {
                    "name": item.get("name", "Unknown"),
                    "price": item.get("price", 0),
                    "id": item.get("id", ""),
                }
                for item in favorites
            ],
            "total_items": len(favorites),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Update the entity."""
        await self.coordinator.async_request_refresh()

