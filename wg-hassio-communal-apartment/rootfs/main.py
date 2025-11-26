#!/usr/bin/env python3
"""Main entry point for Communal Apartment add-on."""
import asyncio
import logging
import sys

from database import Database
from web_server import run_web_server

_LOGGER = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main():
    """Main function."""
    _LOGGER.info("Starting Communal Apartment add-on")
    
    # Initialize database
    db = Database()
    _LOGGER.info("Database initialized")
    
    # Start web server
    await run_web_server(port=8099)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        sys.exit(0)
