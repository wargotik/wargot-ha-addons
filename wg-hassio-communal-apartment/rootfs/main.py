#!/usr/bin/env python3
"""Main entry point for Communal Apartment add-on."""
import asyncio
import logging
import sys

from web_server import run_web_server
from database import Database

_LOGGER = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

WEB_PORT = 8099


async def main():
    """Main function."""
    _LOGGER.info("Starting Communal Apartment add-on")
    
    # Initialize database
    db = Database()
    
    # Start web server
    _LOGGER.info("Starting web server on port %d", WEB_PORT)
    web_runner = await run_web_server(WEB_PORT)
    
    try:
        # Keep running - web server is already running in background
        # Wait forever until interrupted
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour, then check again
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
    finally:
        await web_runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        sys.exit(0)
