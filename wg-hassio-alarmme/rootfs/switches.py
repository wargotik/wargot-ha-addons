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
                "entity_id": "input_boolean.alarmme_away_mode",
                "name": "Away Mode",
                "friendly_name": "Режим отсутствия",
                "icon": "mdi:shield-home",
                "state": "off"
            },
            "night": {
                "entity_id": "input_boolean.alarmme_night_mode",
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
        """Start virtual switches - create them and start monitoring."""
        if not self.ha_token:
            _LOGGER.warning("[switches] SUPERVISOR_TOKEN not found, cannot create switches")
            return False
        
        # Create switches
        success = await self.create_switches()
        
        if success:
            self._connected = True
            # Start monitoring for state changes
            self._monitoring_task = asyncio.create_task(self._monitor_switches())
            _LOGGER.info("[switches] Virtual switches started and monitoring active")
        else:
            _LOGGER.warning("[switches] Failed to create some switches, but continuing...")
            self._connected = True  # Still try to monitor
        
        return success
    
    async def create_switches(self) -> bool:
        """Create input_boolean switches in Home Assistant."""
        if not self.ha_token:
            _LOGGER.warning("[switches] SUPERVISOR_TOKEN not found, cannot create switches")
            return False
        
        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json"
        }
        
        success = True
        for switch_type, switch_data in self.switches.items():
            try:
                # Create input_boolean entity via REST API
                # input_boolean can be created by setting its state
                entity_data = {
                    "state": switch_data["state"],
                    "attributes": {
                        "friendly_name": switch_data["friendly_name"],
                        "icon": switch_data["icon"]
                    }
                }
                
                api_url = f"{self.ha_url}/api/states/{switch_data['entity_id']}"
                _LOGGER.info("[switches] Creating input_boolean: %s", switch_data["entity_id"])
                
                async with session.post(api_url, headers=headers, json=entity_data) as resp:
                    if resp.status in (200, 201):
                        _LOGGER.info("[switches] Successfully created input_boolean: %s", switch_data["entity_id"])
                        # Get current state from response
                        if resp.status == 200:
                            data = await resp.json()
                            switch_data["state"] = data.get("state", "off")
                    else:
                        response_text = await resp.text()
                        _LOGGER.warning("[switches] Failed to create input_boolean %s: status %s, response: %s",
                                      switch_data["entity_id"], resp.status, response_text[:200])
                        # Try to check if it already exists
                        async with session.get(api_url, headers=headers) as check_resp:
                            if check_resp.status == 200:
                                _LOGGER.info("[switches] input_boolean %s already exists", switch_data["entity_id"])
                                data = await check_resp.json()
                                switch_data["state"] = data.get("state", "off")
                            else:
                                success = False
            except Exception as err:
                _LOGGER.error("[switches] Error creating input_boolean %s: %s", switch_data["entity_id"], err, exc_info=True)
                success = False
        
        return success
    
    async def update_switch_state(self, switch_type: str, state: str) -> bool:
        """Update input_boolean state in Home Assistant using services."""
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
            # Use input_boolean service to toggle state
            service = "turn_on" if state.lower() in ("on", "true", "1") else "turn_off"
            service_url = f"{self.ha_url}/api/services/input_boolean/{service}"
            
            service_data = {
                "entity_id": switch_data["entity_id"]
            }
            
            _LOGGER.debug("[switches] Updating input_boolean %s to state: %s (service: %s)", 
                         switch_data["entity_id"], state, service)
            
            async with session.post(service_url, headers=headers, json=service_data) as resp:
                if resp.status == 200:
                    _LOGGER.info("[switches] Successfully updated input_boolean %s to %s", 
                               switch_data["entity_id"], state)
                    switch_data["state"] = state.lower()
                    return True
                else:
                    response_text = await resp.text()
                    _LOGGER.warning("[switches] Failed to update input_boolean %s: status %s, response: %s",
                                  switch_data["entity_id"], resp.status, response_text[:200])
                    return False
        except Exception as err:
            _LOGGER.error("[switches] Error updating input_boolean %s: %s", switch_data["entity_id"], err, exc_info=True)
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

