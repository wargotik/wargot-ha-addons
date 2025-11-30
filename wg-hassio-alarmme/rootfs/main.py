#!/usr/bin/env python3
"""Main entry point for AlarmMe add-on."""
import asyncio
import logging
import sys
import signal

from web_server import run_web_server, send_notification, set_mqtt_switches
from mqtt_switches import MQTTSwitches

_LOGGER = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

mqtt_switches = None


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    _LOGGER.info("Received shutdown signal, stopping...")
    if mqtt_switches:
        mqtt_switches.stop()
    sys.exit(0)


async def main():
    """Main function."""
    global mqtt_switches
    
    _LOGGER.info("Starting AlarmMe add-on")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize MQTT switches
    mqtt_switches = MQTTSwitches()
    if await mqtt_switches.start_async():
        _LOGGER.info("MQTT switches initialized")
        # Pass mqtt_switches to web_server
        set_mqtt_switches(mqtt_switches)
    else:
        _LOGGER.warning("Failed to initialize MQTT switches")
    
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

