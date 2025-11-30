"""Virtual switches management via Home Assistant REST API."""
import asyncio
import aiohttp
import logging
import os
from typing import Dict, Optional, Callable

_LOGGER = logging.getLogger(__name__)


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
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def start(self) -> bool:
        """Start monitoring switches created by integration."""
        if not self.ha_token:
            _LOGGER.warning("[switches] SUPERVISOR_TOKEN not found, cannot monitor switches")
            return False
        
        # Check if switches exist (created by integration)
        switches_exist = await self._check_switches_exist()
        
        if switches_exist:
            self._connected = True
            # Start monitoring for state changes
            self._monitoring_task = asyncio.create_task(self._monitor_switches())
            _LOGGER.info("[switches] Switches monitoring started")
        else:
            _LOGGER.warning("[switches] AlarmMe switches not found. Please install AlarmMe integration first.")
            self._connected = False
        
        return switches_exist
    
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
                        switch_data["state"] = data.get("state", "off")
                        _LOGGER.info("[switches] Found switch: %s (state: %s)", switch_data["entity_id"], switch_data["state"])
                    else:
                        _LOGGER.warning("[switches] Switch not found: %s", switch_data["entity_id"])
                        all_exist = False
            except Exception as err:
                _LOGGER.error("[switches] Error checking switch %s: %s", switch_data["entity_id"], err)
                all_exist = False
        
        return all_exist
    
    async def update_switch_state(self, switch_type: str, state: str) -> bool:
        """Update switch state in Home Assistant using services."""
        if switch_type not in self.switches:
            _LOGGER.error("[switches] Unknown switch type: %s", switch_type)
            return False
        
        if not self.ha_token:
            _LOGGER.warning("[switches] SUPERVISOR_TOKEN not found, cannot update switch")
            return False
        
        switch_data = self.switches[switch_type]
        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Use switch service to toggle state
            service = "turn_on" if state.lower() in ("on", "true", "1") else "turn_off"
            service_url = f"{self.ha_url}/api/services/switch/{service}"
            
            service_data = {
                "entity_id": switch_data["entity_id"]
            }
            
            _LOGGER.debug("[switches] Updating switch %s to state: %s (service: %s)", 
                         switch_data["entity_id"], state, service)
            
            async with session.post(service_url, headers=headers, json=service_data) as resp:
                if resp.status == 200:
                    _LOGGER.info("[switches] Successfully updated switch %s to %s", 
                               switch_data["entity_id"], state)
                    switch_data["state"] = state.lower()
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
        """Monitor switch state changes via polling."""
        while True:
            try:
                for switch_type, switch_data in self.switches.items():
                    old_state = switch_data["state"]
                    new_state = await self.get_switch_state_from_ha(switch_type)
                    
                    if new_state and new_state != old_state:
                        _LOGGER.info("[switches] Switch %s changed from %s to %s", 
                                   switch_data["name"], old_state, new_state)
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
    
    @property
    def is_connected(self) -> bool:
        """Check if switches are connected and monitoring."""
        return self._connected

