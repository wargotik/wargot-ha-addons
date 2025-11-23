#!/usr/bin/env python3
"""Main entry point for Ozon add-on."""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from ozon_api import OzonAPI
from storage import OzonStorage

_LOGGER = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

CONFIG_FILE = "/data/options.json"
SCAN_INTERVAL = 3600  # 1 hour in seconds


def load_config() -> dict:
    """Load configuration from options.json."""
    config_path = Path(CONFIG_FILE)
    if not config_path.exists():
        _LOGGER.error("Configuration file not found: %s", CONFIG_FILE)
        sys.exit(1)
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as err:
        _LOGGER.error("Error loading configuration: %s", err)
        sys.exit(1)


async def main():
    """Main function."""
    _LOGGER.info("Starting Ozon add-on")
    
    # Load configuration
    config = load_config()
    username = config.get("username", "")
    password = config.get("password", "")
    
    if not username or not password:
        _LOGGER.error("Username and password must be configured")
        sys.exit(1)
    
    # Initialize API and storage
    api = OzonAPI(username, password)
    storage = OzonStorage()
    
    # Main loop
    while True:
        try:
            _LOGGER.info("Fetching favorites from Ozon...")
            favorites = await api.get_favorites()
            
            # Save to storage
            storage.save_favorites(favorites)
            
            _LOGGER.info("Fetched %d favorites from Ozon", len(favorites))
            
            # Log favorites
            for item in favorites:
                _LOGGER.info("Item: %s, Price: %s", item.get("name"), item.get("price"))
            
        except Exception as err:
            _LOGGER.error("Error in main loop: %s", err)
        
        # Wait before next update
        await asyncio.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        sys.exit(0)

