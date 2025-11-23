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
from web_server import run_web_server

_LOGGER = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

CONFIG_FILE = "/data/options.json"
SCAN_INTERVAL = 3600  # 1 hour in seconds
WEB_PORT = 8099


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


async def fetch_loop(api: OzonAPI, storage: OzonStorage):
    """Main fetch loop."""
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


async def main():
    """Main function."""
    _LOGGER.info("Starting Ozon add-on")
    
    # Load configuration
    config = load_config()
    site = config.get("site", "ozon.ru")
    
    if not site:
        _LOGGER.error("Site must be configured (ozon.ru or ozon.by)")
        sys.exit(1)
    
    _LOGGER.info("Using Ozon site: %s", site)
    
    # Initialize API and storage
    api = OzonAPI(site)
    storage = OzonStorage()
    
    # Start web server
    _LOGGER.info("Starting web server on port %d", WEB_PORT)
    web_runner = await run_web_server(WEB_PORT)
    
    # Start fetch loop as background task
    fetch_task = asyncio.create_task(fetch_loop(api, storage))
    
    try:
        # Keep running - wait for fetch loop (which runs forever)
        # Web server is already running in background
        await fetch_task
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        fetch_task.cancel()
        try:
            await fetch_task
        except asyncio.CancelledError:
            pass
    finally:
        await web_runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        sys.exit(0)

