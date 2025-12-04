#!/usr/bin/env python3
"""Main entry point for AlarmMe add-on."""
import asyncio
import logging
import sys
import signal

from web_server import run_web_server, send_notification, set_virtual_switches, set_sensor_monitor, get_db, get_sensor_states_cache
from switches import VirtualSwitches
from sensor_monitor import SensorMonitor

_LOGGER = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

virtual_switches = None
sensor_monitor = None


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    _LOGGER.info("Received shutdown signal, stopping...")
    if virtual_switches:
        virtual_switches.stop()
    if sensor_monitor:
        sensor_monitor.stop()
    sys.exit(0)


async def main():
    """Main function."""
    global virtual_switches, sensor_monitor
    
    # Print startup banner
    startup_banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🚨  ALARMME ADD-ON STARTING  🚨                          ║
║                                                                              ║
║                          New Session Started                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(startup_banner)
    _LOGGER.info("=" * 80)
    _LOGGER.info("🚨 ALARMME ADD-ON STARTING - NEW SESSION 🚨")
    _LOGGER.info("=" * 80)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get and save Home Assistant language
    from web_server import get_and_save_ha_language, get_and_save_addon_version
    ha_language = await get_and_save_ha_language()
    _LOGGER.info("Home Assistant language detected and saved: %s", ha_language)
    
    # Get and save add-on version
    addon_version = get_and_save_addon_version()
    _LOGGER.info("Add-on version detected and saved: %s", addon_version)
    
    # Get database and sensor states cache
    db = get_db()
    sensor_states_cache = get_sensor_states_cache()
    
    # Initialize virtual switches via REST API
    virtual_switches = VirtualSwitches()
    if await virtual_switches.start():
        _LOGGER.info("Virtual switches initialized via REST API")
        # Pass virtual_switches to web_server
        set_virtual_switches(virtual_switches)
    else:
        _LOGGER.warning("Failed to initialize virtual switches")
        # Still pass to web_server for UI to show default states
        set_virtual_switches(virtual_switches)
    
    # Initialize and start background sensor monitoring
    from web_server import send_notification
    sensor_monitor = SensorMonitor(db, sensor_states_cache, notification_callback=send_notification)
    if await sensor_monitor.start():
        _LOGGER.info("Background sensor monitoring started")
        set_sensor_monitor(sensor_monitor)
    else:
        _LOGGER.warning("Failed to start background sensor monitoring")
        set_sensor_monitor(sensor_monitor)
    
    # Send notification on startup (mobile devices + persistent notification)
    await send_notification("AlarmMe add-on started", persistent_notification=True, title="AlarmMe")
    
    # Start web server
    await run_web_server(port=8099)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
        sys.exit(0)

