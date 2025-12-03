"""Virtual switches management via Home Assistant REST API."""
import asyncio
import aiohttp
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Callable

_LOGGER = logging.getLogger(__name__)

# Path to local state storage file
STATE_FILE = "/data/switches_state.json"


class VirtualSwitches:
    """Manage virtual switches via Home Assistant REST API."""
    
    def __init__(self):
        """Initialize virtual switches manager."""
        self.ha_token = os.environ.get("SUPERVISOR_TOKEN")
        self.ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        self.switches = {
            "away": {
                "entity_id": "switch.alarmme_away_mode",
                "unique_id": "alarmme_away_mode",
                "name": "Away Mode",
                "friendly_name": "Режим отсутствия",
                "icon": "mdi:shield-home",
                "state": "off"
            },
            "night": {
                "entity_id": "switch.alarmme_night_mode",
                "unique_id": "alarmme_night_mode",
                "name": "Night Mode",
                "friendly_name": "Ночной режим",
                "icon": "mdi:weather-night",
                "state": "off"
            }
        }
        self._session: Optional[aiohttp.ClientSession] = None
        self.state_callback: Optional[Callable[[str, str], None]] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        self._connected = False
        self._state_file = Path(STATE_FILE)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def start(self) -> bool:
        """Start monitoring switches created by integration."""
        # Load local state first (before checking HA)
        self._load_states()
        
        if not self.ha_token:
            _LOGGER.warning("[switches] SUPERVISOR_TOKEN not found, cannot monitor switches")
            # Still return True if we have local state
            return True
        
        # Check if switches exist (created by integration)
        switches_exist = await self._check_switches_exist()
        
        if switches_exist:
            self._connected = True
            # Start monitoring for state changes
            self._monitoring_task = asyncio.create_task(self._monitor_switches())
            _LOGGER.info("[switches] Switches monitoring started")
        else:
            _LOGGER.warning("[switches] AlarmMe switches not found. Please install AlarmMe integration first.")
            _LOGGER.info("[switches] Using local state storage")
            self._connected = False
        
        return True  # Always return True if we have local state
    
    async def _check_switches_exist(self) -> bool:
        """Check if switches created by integration exist."""
        if not self.ha_token:
            return False
        
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {self.ha_token}"}
        
        all_exist = True
        for switch_type, switch_data in self.switches.items():
            try:
                api_url = f"{self.ha_url}/api/states/{switch_data['entity_id']}"
                async with session.get(api_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        new_state = data.get("state", "off")
                        switch_data["state"] = new_state
                        _LOGGER.info("[switches] Found switch: %s (state: %s)", switch_data["entity_id"], new_state)
                        # Save state to local storage
                        self._save_states()
                    else:
                        _LOGGER.warning("[switches] Switch not found: %s", switch_data["entity_id"])
                        all_exist = False
            except Exception as err:
                _LOGGER.error("[switches] Error checking switch %s: %s", switch_data["entity_id"], err)
                all_exist = False
        
        return all_exist
    
    async def update_switch_state(self, switch_type: str, state: str) -> bool:
        """Update switch state in Home Assistant using services.
        
        Switches are mutually exclusive: if one is turned on, the other is turned off.
        """
        if switch_type not in self.switches:
            _LOGGER.error("[switches] Unknown switch type: %s", switch_type)
            return False
        
        if not self.ha_token:
            _LOGGER.warning("[switches] SUPERVISOR_TOKEN not found, cannot update switch")
            return False
        
        target_state = state.lower() in ("on", "true", "1")
        other_switch_type = "night" if switch_type == "away" else "away"
        switch_data = self.switches[switch_type]
        
        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # If turning on this switch, turn off the other one
            if target_state:
                # Turn off the other switch first
                other_switch_data = self.switches[other_switch_type]
                service_url = f"{self.ha_url}/api/services/switch/turn_off"
                service_data = {"entity_id": other_switch_data["entity_id"]}
                
                async with session.post(service_url, headers=headers, json=service_data) as resp:
                    if resp.status == 200:
                        other_switch_data["state"] = "off"
                        _LOGGER.info("[switches] Turned off %s (mutually exclusive)", other_switch_data["name"])
                    else:
                        _LOGGER.warning("[switches] Failed to turn off %s: status %s",
                                      other_switch_data["entity_id"], resp.status)
                
                # Now turn on the target switch
                service_url = f"{self.ha_url}/api/services/switch/turn_on"
                service_data = {"entity_id": switch_data["entity_id"]}
            else:
                # Just turn off the target switch
                service_url = f"{self.ha_url}/api/services/switch/turn_off"
                service_data = {"entity_id": switch_data["entity_id"]}
            
            _LOGGER.debug("[switches] Updating switch %s to state: %s", 
                         switch_data["entity_id"], "on" if target_state else "off")
            
            async with session.post(service_url, headers=headers, json=service_data) as resp:
                if resp.status == 200:
                    switch_data["state"] = "on" if target_state else "off"
                    _LOGGER.info("[switches] Successfully updated switch %s to %s", 
                               switch_data["entity_id"], switch_data["state"])
                    # Save state to local storage
                    self._save_states()
                    return True
                else:
                    response_text = await resp.text()
                    _LOGGER.warning("[switches] Failed to update switch %s: status %s, response: %s",
                                  switch_data["entity_id"], resp.status, response_text[:200])
                    return False
        except Exception as err:
            _LOGGER.error("[switches] Error updating switch %s: %s", switch_data["entity_id"], err, exc_info=True)
            return False
    
    async def get_switch_state_from_ha(self, switch_type: str) -> Optional[str]:
        """Get current switch state from Home Assistant API."""
        if switch_type not in self.switches:
            _LOGGER.error("[switches] Unknown switch type: %s", switch_type)
            return None
        
        if not self.ha_token:
            _LOGGER.warning("[switches] SUPERVISOR_TOKEN not found, cannot get switch state")
            return None
        
        switch_data = self.switches[switch_type]
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {self.ha_token}"}
        
        try:
            api_url = f"{self.ha_url}/api/states/{switch_data['entity_id']}"
            async with session.get(api_url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    state = data.get("state", "unknown")
                    switch_data["state"] = state
                    # Save state to local storage
                    self._save_states()
                    return state
                else:
                    _LOGGER.warning("[switches] Failed to get switch state %s: status %s",
                                  switch_data["entity_id"], resp.status)
                    return None
        except Exception as err:
            _LOGGER.error("[switches] Error getting switch state %s: %s", switch_data["entity_id"], err, exc_info=True)
            return None
    
    def get_switch_state(self, switch_type: str) -> Optional[str]:
        """Get current switch state from local cache."""
        if switch_type in self.switches:
            return self.switches[switch_type]["state"]
        return None
    
    async def _monitor_switches(self):
        """Monitor switch state changes via polling.
        
        Ensures mutual exclusivity: if one switch is turned on, the other is turned off.
        """
        while True:
            try:
                for switch_type, switch_data in self.switches.items():
                    old_state = switch_data["state"]
                    new_state = await self.get_switch_state_from_ha(switch_type)
                    
                    if new_state and new_state != old_state:
                        _LOGGER.info("[switches] Switch %s changed from %s to %s", 
                                   switch_data["name"], old_state, new_state)
                        
                        # If this switch was turned on, ensure the other is off
                        if new_state.lower() == "on":
                            other_switch_type = "night" if switch_type == "away" else "away"
                            other_switch_data = self.switches[other_switch_type]
                            
                            # Check if other switch is also on
                            other_state = await self.get_switch_state_from_ha(other_switch_type)
                            if other_state and other_state.lower() == "on":
                                # Turn off the other switch
                                _LOGGER.info("[switches] Ensuring mutual exclusivity: turning off %s", 
                                           other_switch_data["name"])
                                await self.update_switch_state(other_switch_type, "off")
                        
                        # Save state to local storage
                        self._save_states()
                        if self.state_callback:
                            self.state_callback(switch_type, new_state.upper())
                
                await asyncio.sleep(2)  # Poll every 2 seconds
            except asyncio.CancelledError:
                _LOGGER.info("[switches] Monitoring task cancelled")
                break
            except Exception as err:
                _LOGGER.error("[switches] Error monitoring switches: %s", err, exc_info=True)
                await asyncio.sleep(10)
    
    def get_all_states(self) -> Dict[str, str]:
        """Get all switch states from local cache."""
        return {switch_type: switch_data["state"].upper() for switch_type, switch_data in self.switches.items()}
    
    def get_current_mode(self) -> str:
        """Get current mode: 'off', 'away', or 'night'.
        
        Returns:
            'off' - both switches are off
            'away' - away mode is on
            'night' - night mode is on
        """
        away_state = self.switches["away"]["state"].lower()
        night_state = self.switches["night"]["state"].lower()
        
        # Ensure mutual exclusivity: if both are on, prioritize away
        if away_state == "on":
            return "away"
        elif night_state == "on":
            return "night"
        else:
            return "off"
    
    def stop(self):
        """Stop monitoring and close session."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
        self._connected = False
        _LOGGER.info("[switches] Virtual switches stopped")
    
    async def close(self):
        """Close aiohttp session."""
        self.stop()
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _load_states(self) -> None:
        """Load switch states from local storage file."""
        if not self._state_file.exists():
            _LOGGER.debug("[switches] State file not found, using default states")
            return
        
        try:
            with open(self._state_file, 'r', encoding='utf-8') as f:
                saved_states = json.load(f)
            
            # Restore states for each switch
            for switch_type, switch_data in self.switches.items():
                if switch_type in saved_states:
                    saved_state = saved_states[switch_type].lower()
                    if saved_state in ("on", "off"):
                        switch_data["state"] = saved_state
                        _LOGGER.info("[switches] Loaded local state for %s: %s", 
                                   switch_data["name"], saved_state)
                    else:
                        _LOGGER.warning("[switches] Invalid state '%s' for %s, using default", 
                                      saved_state, switch_data["name"])
            
            _LOGGER.info("[switches] Loaded switch states from local storage")
        except json.JSONDecodeError as err:
            _LOGGER.warning("[switches] Error parsing state file: %s. Using default states.", err)
        except Exception as err:
            _LOGGER.error("[switches] Error loading state file: %s. Using default states.", err, exc_info=True)
    
    def _save_states(self) -> None:
        """Save switch states to local storage file."""
        try:
            # Ensure /data directory exists
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing state if file exists (to preserve last_sensor_poll)
            state_data = {}
            if self._state_file.exists():
                try:
                    with open(self._state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                except Exception:
                    state_data = {}
            
            # Update switch states
            for switch_type, switch_data in self.switches.items():
                state_data[switch_type] = switch_data["state"]
            
            # Write to file atomically
            temp_file = self._state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            # Replace original file
            temp_file.replace(self._state_file)
            _LOGGER.debug("[switches] Saved switch states to local storage")
        except Exception as err:
            _LOGGER.error("[switches] Error saving state file: %s", err, exc_info=True)
    
    @property
    def is_connected(self) -> bool:
        """Check if switches are connected and monitoring."""
        return self._connected

