"""API client for Ozon."""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class OzonAPI:
    """Class to interact with Ozon via direct links."""

    def __init__(self, site: str) -> None:
        """Initialize Ozon API client."""
        self.site = site
        self.base_url = f"https://{site}"

    async def get_favorites(self) -> list[dict[str, Any]]:
        """Get favorite items from Ozon by fetching pages directly."""
        try:
            # TODO: Implement fetching favorites from Ozon
            # This should fetch pages directly without authentication
            # Example structure:
            # - Fetch page from Ozon (e.g., wishlist page)
            # - Parse HTML/JSON response
            # - Extract items with name and price
            # - Return list of items
            
            _LOGGER.debug("Fetching favorites from Ozon (%s)", self.site)
            
            # Placeholder - replace with actual page fetching
            # import aiohttp
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(f"{self.base_url}/some-page") as response:
            #         html = await response.text()
            #         # Parse HTML and extract items
            #         items = parse_items(html)
            #         return items
            
            # Temporary mock data for testing
            return [
                {
                    "name": "Test Item 1",
                    "price": 1000,
                    "id": "1",
                    "url": f"{self.base_url}/product/test-item-1/"
                },
                {
                    "name": "Test Item 2",
                    "price": 2000,
                    "id": "2",
                    "url": f"{self.base_url}/product/test-item-2/"
                },
            ]
        except Exception as err:
            _LOGGER.error("Error fetching favorites: %s", err)
            return []

