#!/usr/bin/env python3
"""Main entry point for AlarmMe add-on."""
import asyncio
import logging
import sys

from web_server import run_web_server, send_notification

_LOGGER = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main():
    """Main function."""
    _LOGGER.info("Starting AlarmMe add-on")
    
    # Send notification on startup
    await send_notification("mobile_app_iphone", "AlarmMe add-on started")
    
    # Start web server
    await run_web_server(port=8099)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        sys.exit(0)

