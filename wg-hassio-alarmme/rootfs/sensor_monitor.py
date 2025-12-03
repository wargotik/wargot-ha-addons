"""Background sensor monitoring."""
import asyncio
import aiohttp
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

_LOGGER = logging.getLogger(__name__)

# Path to state storage file (same as switches)
STATE_FILE = "/data/switches_state.json"


class SensorMonitor:
    """Background monitor for sensors."""
    
    def __init__(self, database, sensor_states_cache):
        """Initialize sensor monitor."""
        self.ha_token = os.environ.get("SUPERVISOR_TOKEN")
        self.ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        self._db = database
        self._sensor_states_cache = sensor_states_cache
        self._monitoring_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._state_file = Path(STATE_FILE)
        self._running = False
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def _poll_sensors(self):
        """Poll sensors from Home Assistant API."""
        if not self.ha_token:
            _LOGGER.debug("[sensor_monitor] SUPERVISOR_TOKEN not found, skipping poll")
            return
        
        try:
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {self.ha_token}"}
            api_url = f"{self.ha_url}/api/states"
            
            async with session.get(api_url, headers=headers) as resp:
                if resp.status == 200:
                    states = await resp.json()
                    
                    for state in states:
                        entity_id = state.get("entity_id", "")
                        attributes = state.get("attributes", {})
                        device_class = attributes.get("device_class", "")
                        friendly_name = attributes.get("friendly_name", entity_id)
                        
                        # Only process motion, moving, occupancy, presence sensors
                        if device_class not in ("motion", "moving", "occupancy", "presence"):
                            continue
                        
                        # Check if sensor is saved in database
                        saved_sensor = self._db.get_sensor(entity_id)
                        
                        # Auto-save sensor if not in database
                        if not saved_sensor:
                            self._db.save_sensor(
                                entity_id=entity_id,
                                name=friendly_name,
                                device_class=device_class,
                                enabled_in_away_mode=False,
                                enabled_in_night_mode=False
                            )
                            saved_sensor = self._db.get_sensor(entity_id)
                        
                        # Track sensor state changes for trigger detection
                        current_state = state.get("state", "unknown").lower()
                        previous_state = self._sensor_states_cache.get(entity_id, "unknown")
                        
                        # Detect trigger: state changed from off to on
                        if previous_state == "off" and current_state == "on":
                            _LOGGER.info("[sensor_monitor] 🔔 Sensor TRIGGERED: %s (%s) - changed from %s to %s", 
                                       friendly_name, entity_id, previous_state, current_state)
                            # Record trigger in database
                            self._db.record_sensor_trigger(entity_id)
                        
                        # Update cache with current state
                        self._sensor_states_cache[entity_id] = current_state
                    
                    # Save last poll time
                    self._save_last_poll_time()
                    _LOGGER.debug("[sensor_monitor] Polled %d sensors, saved poll time", len([s for s in states if s.get("attributes", {}).get("device_class") in ("motion", "moving", "occupancy", "presence")]))
                else:
                    _LOGGER.warning("[sensor_monitor] HA API returned status %s", resp.status)
                    
        except Exception as err:
            _LOGGER.error("[sensor_monitor] Error polling sensors: %s", err, exc_info=True)
    
    def _save_last_poll_time(self):
        """Save last poll time to JSON file."""
        try:
            # Ensure directory exists
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing state if file exists
            state_data = {}
            if self._state_file.exists():
                try:
                    with open(self._state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                except Exception:
                    state_data = {}
            
            # Update last sensor poll time (use UTC with 'Z' suffix for proper ISO format)
            poll_time = datetime.utcnow().isoformat() + 'Z'
            state_data["last_sensor_poll"] = poll_time
            
            # Write to file atomically
            temp_file = self._state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            # Replace original file
            temp_file.replace(self._state_file)
            _LOGGER.debug("[sensor_monitor] Saved last poll time: %s", poll_time)
        except Exception as err:
            _LOGGER.error("[sensor_monitor] Error saving last poll time: %s", err, exc_info=True)
    
    def get_last_poll_time(self) -> Optional[str]:
        """Get last poll time from JSON file."""
        try:
            if not self._state_file.exists():
                return None
            
            with open(self._state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                return state_data.get("last_sensor_poll")
        except Exception as err:
            _LOGGER.debug("[sensor_monitor] Error reading last poll time: %s", err)
            return None
    
    async def _monitor_loop(self):
        """Background monitoring loop."""
        _LOGGER.info("[sensor_monitor] Starting background sensor monitoring (every 5 seconds)")
        poll_count = 0
        while self._running:
            try:
                poll_count += 1
                _LOGGER.debug("[sensor_monitor] Polling sensors (iteration #%d)", poll_count)
                await self._poll_sensors()
                await asyncio.sleep(5)  # Poll every 5 seconds
            except asyncio.CancelledError:
                _LOGGER.info("[sensor_monitor] Monitoring task cancelled")
                break
            except Exception as err:
                _LOGGER.error("[sensor_monitor] Error in monitoring loop: %s", err, exc_info=True)
                await asyncio.sleep(10)  # Wait longer on error
    
    async def start(self) -> bool:
        """Start background monitoring."""
        if not self.ha_token:
            _LOGGER.warning("[sensor_monitor] SUPERVISOR_TOKEN not found, cannot start monitoring")
            return False
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        _LOGGER.info("[sensor_monitor] Background sensor monitoring started")
        return True
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        _LOGGER.info("[sensor_monitor] Background sensor monitoring stopped")
    
    async def close(self):
        """Close aiohttp session."""
        self.stop()
        if self._session and not self._session.closed:
            await self._session.close()

