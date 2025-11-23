"""Storage for Ozon add-on."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

STORAGE_FILE = "/data/ozon_storage.json"


class OzonStorage:
    """Handle storage for Ozon add-on."""

    def __init__(self) -> None:
        """Initialize storage."""
        self.storage_path = Path(STORAGE_FILE)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        """Load data from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data
            return {"favorites": []}
        except Exception as err:
            _LOGGER.error("Error loading storage: %s", err)
            return {"favorites": []}

    def save(self, data: dict[str, Any]) -> None:
        """Save data to storage."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as err:
            _LOGGER.error("Error saving storage: %s", err)

    def save_favorites(self, favorites: list[dict[str, Any]]) -> None:
        """Save favorites to storage."""
        data = self.load()
        data["favorites"] = favorites
        self.save(data)

    def get_favorites(self) -> list[dict[str, Any]]:
        """Get favorites from storage."""
        data = self.load()
        return data.get("favorites", [])

