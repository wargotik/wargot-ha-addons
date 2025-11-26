#!/usr/bin/env python3
"""Main entry point for Communal Apartment add-on."""
import asyncio
import json
import logging
import sys
from pathlib import Path

from database import Database
from web_server import run_web_server

_LOGGER = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

CONFIG_FILE = "/data/options.json"


def load_config() -> dict:
    """Load configuration from options.json."""
    config_path = Path(CONFIG_FILE)
    if not config_path.exists():
        _LOGGER.warning("Configuration file not found: %s, using defaults", CONFIG_FILE)
        return {"currency": "EUR"}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as err:
        _LOGGER.error("Error loading configuration: %s, using defaults", err)
        return {"currency": "EUR"}


async def main():
    """Main function."""
    _LOGGER.info("Starting Communal Apartment add-on")
    
    # Load configuration
    config = load_config()
    currency = config.get("currency", "EUR")
    _LOGGER.info("Configuration loaded: currency=%s", currency)
    
    # Initialize database
    db = Database()
    _LOGGER.info("Database initialized")
    
    # Start web server
    await run_web_server(port=8099, currency=currency)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        sys.exit(0)
