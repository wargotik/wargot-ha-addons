"""Storage for Ozon add-on using SQLite."""
from __future__ import annotations

import logging
from typing import Any

from database import Database

_LOGGER = logging.getLogger(__name__)


class OzonStorage:
    """Handle storage for Ozon add-on using SQLite database."""

    def __init__(self) -> None:
        """Initialize storage."""
        self.db = Database()

    def save_favorites(self, favorites: list[dict[str, Any]]) -> None:
        """Save favorites to database."""
        try:
            for item in favorites:
                product_id = item.get("id", "")
                url = item.get("url", "")
                name = item.get("name", "")
                price = item.get("price", 0)
                
                if product_id and url:
                    self.db.add_product(product_id, url, name, price)
                else:
                    _LOGGER.warning("Skipping invalid item: %s", item)
        except Exception as err:
            _LOGGER.error("Error saving favorites: %s", err)

    def get_favorites(self) -> list[dict[str, Any]]:
        """Get favorites from database."""
        try:
            return self.db.get_all_products()
        except Exception as err:
            _LOGGER.error("Error getting favorites: %s", err)
            return []

