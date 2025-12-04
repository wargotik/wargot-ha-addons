"""Background sensor monitoring."""
import asyncio
import aiohttp
import json
import logging
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from pprint import pformat

_LOGGER = logging.getLogger(__name__)

# Path to state storage file (same as switches)
STATE_FILE = "/data/switches_state.json"


class SensorMonitor:
    """Background monitor for sensors."""
    
    def __init__(self, database, sensor_states_cache, notification_callback=None):
        """Initialize sensor monitor."""
        self.ha_token = os.environ.get("SUPERVISOR_TOKEN")
        self.ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        self._db = database
        self._sensor_states_cache = sensor_states_cache
        self._notification_callback = notification_callback
        self._monitoring_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._state_file = Path(STATE_FILE)
        self._running = False
        self._areas_cache: Dict[str, str] = {}  # Cache for area_id -> area_name mapping
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    def _check_camera_motion(self, attributes: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check if camera has detected motion based on motion_video_time attribute.
        Returns: (has_motion: bool, motion_time: Optional[str])
        """
        try:
            # Check if motion detection is enabled
            motion_detection = attributes.get("motion_detection", False)
            if not motion_detection:
                return False, None
            
            # Get motion_video_time from attributes
            motion_video_time = attributes.get("motion_video_time")
            if not motion_video_time:
                return False, None
            
            # Parse motion_video_time (format: "2025-12-04 13:04:59.450000")
            try:
                # Try parsing with microseconds
                if isinstance(motion_video_time, str):
                    # Remove microseconds if present
                    motion_time_str = motion_video_time.split('.')[0]
                    motion_dt = datetime.strptime(motion_time_str, "%Y-%m-%d %H:%M:%S")
                else:
                    return False, None
                
                # Check if motion was detected in last 60 seconds
                now = datetime.now()
                time_diff = (now - motion_dt).total_seconds()
                
                if 0 <= time_diff <= 60:
                    return True, motion_video_time
                else:
                    return False, motion_video_time
            except (ValueError, TypeError) as parse_err:
                _LOGGER.debug("[sensor_monitor] Error parsing motion_video_time '%s': %s", motion_video_time, parse_err)
                return False, None
        except Exception as err:
            _LOGGER.debug("[sensor_monitor] Error checking camera motion: %s", err)
            return False, None
    
    async def _get_area_for_entity(self, entity_id: str) -> Optional[str]:
        """Get area name for entity from Home Assistant Entity Registry and Areas."""
        try:
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {self.ha_token}"}
            
            # Get entity registry to find area_id
            entity_registry_url = f"{self.ha_url}/api/config/entity_registry/{entity_id}"
            async with session.get(entity_registry_url, headers=headers) as resp:
                if resp.status == 200:
                    entity_data = await resp.json()
                    area_id = entity_data.get("area_id")
                    
                    if not area_id:
                        return None
                    
                    # Check cache first
                    if area_id in self._areas_cache:
                        return self._areas_cache[area_id]
                    
                    # Get area name from areas API
                    areas_url = f"{self.ha_url}/api/config/area_registry"
                    async with session.get(areas_url, headers=headers) as areas_resp:
                        if areas_resp.status == 200:
                            areas = await areas_resp.json()
                            for area in areas:
                                if area.get("area_id") == area_id:
                                    area_name = area.get("name", area_id)
                                    # Cache it
                                    self._areas_cache[area_id] = area_name
                                    return area_name
                elif resp.status == 404:
                    # Entity not found in registry, that's ok
                    return None
                else:
                    _LOGGER.debug("[sensor_monitor] Failed to get entity registry for %s: status %s", entity_id, resp.status)
                    return None
        except Exception as err:
            _LOGGER.debug("[sensor_monitor] Error getting area for entity %s: %s", entity_id, err)
            return None
    
    async def _poll_sensors(self):
        """Poll sensors from Home Assistant API."""
        if not self.ha_token:
            _LOGGER.warning("[sensor_monitor] SUPERVISOR_TOKEN not found, skipping poll")
            return
        
        try:
            _LOGGER.info("[sensor_monitor] Starting sensor poll from HA API: %s", self.ha_url)
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {self.ha_token}"}
            api_url = f"{self.ha_url}/api/states"
            
            async with session.get(api_url, headers=headers) as resp:
                if resp.status == 200:
                    states = await resp.json()
                    _LOGGER.debug("[sensor_monitor] Received %d total states from HA API", len(states))
                    
                    processed_count = 0
                    new_sensors_count = 0
                    trigger_count = 0
                    
                    for state in states:
                        entity_id = state.get("entity_id", "")
                        attributes = state.get("attributes", {})
                        device_class = attributes.get("device_class", "")
                        friendly_name = attributes.get("friendly_name", entity_id)
                        current_state = state.get("state", "unknown")
                        
                        # Check if this is a camera entity with motion detection
                        is_camera = entity_id.startswith("camera.")
                        camera_has_motion = False
                        camera_motion_time = None
                        
                        if is_camera:
                            # Check camera motion detection
                            camera_has_motion, camera_motion_time = self._check_camera_motion(attributes)
                            if camera_has_motion or camera_motion_time:
                                # Treat camera as "moving" device_class
                                device_class = "moving"
                                # Set state based on motion detection
                                current_state = "on" if camera_has_motion else "off"
                                _LOGGER.debug("[sensor_monitor] Camera %s: motion_detected=%s, motion_time=%s", 
                                            entity_id, camera_has_motion, camera_motion_time)
                        
                        # Only process motion, moving, occupancy, presence sensors OR cameras with motion detection
                        if device_class not in ("motion", "moving", "occupancy", "presence"):
                            continue
                        
                        processed_count += 1
                        
                        # Log all sensor information received from HA (entire state object)
                        _LOGGER.info("[sensor_monitor] Sensor from HA - Full data for %s:\n%s", 
                                    entity_id, pformat(state, width=120, indent=2))
                        
                        # Check if sensor is saved in database
                        saved_sensor = self._db.get_sensor(entity_id)
                        
                        # Get area for sensor
                        area_name = await self._get_area_for_entity(entity_id)
                        
                            # Auto-save sensor if not in database
                        if not saved_sensor:
                            _LOGGER.info("[sensor_monitor] Auto-saving new sensor: %s (%s) - %s - area: %s", 
                                       friendly_name, entity_id, device_class, area_name or "None")
                            self._db.save_sensor(
                                entity_id=entity_id,
                                name=friendly_name,
                                device_class=device_class,
                                enabled_in_away_mode=False,
                                enabled_in_night_mode=False,
                                enabled_in_perimeter_mode=False,
                                area=area_name
                            )
                            saved_sensor = self._db.get_sensor(entity_id)
                            new_sensors_count += 1
                        elif area_name and (not saved_sensor.get("area") or saved_sensor.get("area") != area_name):
                            # Update area if it changed or wasn't set before
                            _LOGGER.debug("[sensor_monitor] Updating area for sensor %s: %s -> %s", 
                                        entity_id, saved_sensor.get("area"), area_name)
                            # Update area in database
                            conn = self._db._db_path  # Access db_path
                            import sqlite3
                            try:
                                conn_db = sqlite3.connect(self._db.db_path)
                                cursor = conn_db.cursor()
                                cursor.execute("UPDATE sensors SET area = ?, updated_at = CURRENT_TIMESTAMP WHERE entity_id = ?", 
                                              (area_name, entity_id))
                                conn_db.commit()
                                conn_db.close()
                            except Exception as update_err:
                                _LOGGER.debug("[sensor_monitor] Error updating area: %s", update_err)
                        
                        # Detect trigger: sensor is in "on" state
                        # For cameras, we already set current_state above
                        if not is_camera:
                            current_state = state.get("state", "unknown").lower()
                        else:
                            current_state = current_state.lower()
                        
                        # Record trigger if sensor is active (on/true)
                        if current_state in ("on", "true"):
                            # For cameras, use motion_video_time as trigger time
                            if is_camera and camera_motion_time:
                                # Convert motion_video_time to ISO format for database
                                try:
                                    motion_time_str = camera_motion_time.split('.')[0]
                                    motion_dt = datetime.strptime(motion_time_str, "%Y-%m-%d %H:%M:%S")
                                    last_changed = motion_dt.isoformat() + 'Z'
                                except Exception:
                                    last_changed = state.get("last_changed")
                            else:
                                # Get last_changed from HA (when HA detected the state change)
                                last_changed = state.get("last_changed")
                            
                            _LOGGER.info("[sensor_monitor] 🔔 Sensor TRIGGERED: %s (%s) - state: %s, last_changed: %s", 
                                       friendly_name, entity_id, current_state, last_changed)
                            # Record trigger in database with last_changed from HA
                            if self._db.record_sensor_trigger(entity_id, last_changed):
                                trigger_count += 1
                                _LOGGER.info("[sensor_monitor] ✅ Recorded trigger in database for: %s (last_changed: %s)", 
                                           entity_id, last_changed)
                            else:
                                _LOGGER.error("[sensor_monitor] ❌ Failed to record trigger in database for: %s", entity_id)
                            
                            # Check for intrusion: sensor triggered while add-on is in active mode
                            if saved_sensor:
                                current_mode = self._get_current_addon_mode()
                                sensor_enabled_in_mode = False
                                
                                if current_mode == "away":
                                    sensor_enabled_in_mode = bool(saved_sensor.get("enabled_in_away_mode", False))
                                elif current_mode == "night":
                                    sensor_enabled_in_mode = bool(saved_sensor.get("enabled_in_night_mode", False))
                                elif current_mode == "perimeter":
                                    sensor_enabled_in_mode = bool(saved_sensor.get("enabled_in_perimeter_mode", False))
                                
                                if current_mode in ("away", "night", "perimeter") and sensor_enabled_in_mode:
                                    # INTRUSION DETECTED!
                                    # Get area from saved sensor or fetch it
                                    sensor_area = saved_sensor.get("area") if saved_sensor else None
                                    if not sensor_area:
                                        sensor_area = await self._get_area_for_entity(entity_id)
                                    
                                    # Format intrusion message with area
                                    if sensor_area:
                                        intrusion_message = f"⚠️ ПРОНИКНОВЕНИЕ {sensor_area}! Сработал датчик: {friendly_name}"
                                    else:
                                        intrusion_message = f"⚠️ ПРОНИКНОВЕНИЕ! Сработал датчик: {friendly_name}"
                                    
                                    _LOGGER.error("[sensor_monitor] 🚨 INTRUSION DETECTED: %s (%s) - Mode: %s, Sensor enabled in mode: %s, Area: %s", 
                                                friendly_name, entity_id, current_mode, sensor_enabled_in_mode, sensor_area or "None")
                                    
                                    if self._notification_callback:
                                        _LOGGER.info("[sensor_monitor] Calling notification callback to send alert")
                                        # Add actionable button to silence alarm
                                        actions = [
                                            {
                                                "action": "SILENCE_ALARM",
                                                "title": "Отключить тревогу"
                                            }
                                        ]
                                        try:
                                            result = await self._notification_callback(
                                                intrusion_message, 
                                                persistent_notification=True, 
                                                title="🚨 ТРЕВОГА",
                                                actions=actions
                                            )
                                            _LOGGER.info("[sensor_monitor] Notification callback returned: %s", result)
                                        except Exception as notif_err:
                                            _LOGGER.error("[sensor_monitor] Error calling notification callback: %s", notif_err, exc_info=True)
                                    else:
                                        _LOGGER.warning("[sensor_monitor] No notification callback set, cannot send intrusion alert!")
                    
                    # Save last poll time
                    self._save_last_poll_time()
                    _LOGGER.info("[sensor_monitor] ✅ Poll completed: processed %d sensors, %d new sensors, %d triggers detected", 
                               processed_count, new_sensors_count, trigger_count)
                else:
                    _LOGGER.warning("[sensor_monitor] ❌ HA API returned status %s (expected 200)", resp.status)
                    response_text = await resp.text()
                    _LOGGER.debug("[sensor_monitor] Response body: %s", response_text[:200])
                    
        except Exception as err:
            _LOGGER.error("[sensor_monitor] ❌ Error polling sensors: %s", err, exc_info=True)
    
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
    
    def _get_current_addon_mode(self) -> str:
        """Get current add-on mode from switches state file."""
        try:
            if not self._state_file.exists():
                return "off"
            
            with open(self._state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                
                # Switches are stored directly in root: "away": "on", "night": "off", "perimeter": "off"
                away_state = state_data.get("away", "off").lower()
                night_state = state_data.get("night", "off").lower()
                perimeter_state = state_data.get("perimeter", "off").lower()
                
                if away_state == "on":
                    return "away"
                elif night_state == "on":
                    return "night"
                elif perimeter_state == "on":
                    return "perimeter"
                else:
                    return "off"
        except Exception as err:
            _LOGGER.debug("[sensor_monitor] Error reading current mode: %s", err)
            return "off"
    
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

