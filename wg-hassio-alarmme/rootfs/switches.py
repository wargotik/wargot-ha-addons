"""Virtual switches management via Home Assistant REST API."""
import asyncio
import aiohttp
import logging
import os
from typing import Dict, Optional

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
                "name": "Away Mode",
                "friendly_name": "Режим отсутствия",
                "state": "off"
            },
            "night": {
                "entity_id": "switch.alarmme_night_mode",
                "name": "Night Mode",
                "friendly_name": "Ночной режим",
                "state": "off"
            }
        }
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def create_switches(self) -> bool:
        """Create virtual switches in Home Assistant."""
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
                # Create switch entity via REST API
                entity_data = {
                    "state": switch_data["state"],
                    "attributes": {
                        "friendly_name": switch_data["friendly_name"],
                        "icon": "mdi:shield-home" if switch_type == "away" else "mdi:weather-night"
                    }
                }
                
                api_url = f"{self.ha_url}/api/states/{switch_data['entity_id']}"
                _LOGGER.info("[switches] Creating switch: %s", switch_data["entity_id"])
                
                async with session.post(api_url, headers=headers, json=entity_data) as resp:
                    if resp.status in (200, 201):
                        _LOGGER.info("[switches] Successfully created switch: %s", switch_data["entity_id"])
                    else:
                        response_text = await resp.text()
                        _LOGGER.warning("[switches] Failed to create switch %s: status %s, response: %s",
                                      switch_data["entity_id"], resp.status, response_text[:200])
                        success = False
            except Exception as err:
                _LOGGER.error("[switches] Error creating switch %s: %s", switch_data["entity_id"], err, exc_info=True)
                success = False
        
        return success
    
    async def update_switch_state(self, switch_type: str, state: str) -> bool:
        """Update switch state in Home Assistant."""
        if switch_type not in self.switches:
            _LOGGER.error("[switches] Unknown switch type: %s", switch_type)
            return False
        
        if not self.ha_token:
            _LOGGER.warning("[switches] SUPERVISOR_TOKEN not found, cannot update switch")
            return False
        
        switch_data = self.switches[switch_type]
        switch_data["state"] = state
        
        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json"
        }
        
        try:
            entity_data = {
                "state": state,
                "attributes": {
                    "friendly_name": switch_data["friendly_name"],
                    "icon": "mdi:shield-home" if switch_type == "away" else "mdi:weather-night"
                }
            }
            
            api_url = f"{self.ha_url}/api/states/{switch_data['entity_id']}"
            _LOGGER.debug("[switches] Updating switch %s to state: %s", switch_data["entity_id"], state)
            
            async with session.post(api_url, headers=headers, json=entity_data) as resp:
                if resp.status in (200, 201):
                    _LOGGER.info("[switches] Successfully updated switch %s to %s", switch_data["entity_id"], state)
                    return True
                else:
                    response_text = await resp.text()
                    _LOGGER.warning("[switches] Failed to update switch %s: status %s, response: %s",
                                  switch_data["entity_id"], resp.status, response_text[:200])
                    return False
        except Exception as err:
            _LOGGER.error("[switches] Error updating switch %s: %s", switch_data["entity_id"], err, exc_info=True)
            return False
    
    async def get_switch_state(self, switch_type: str) -> Optional[str]:
        """Get current switch state from Home Assistant."""
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
    
    async def monitor_switches(self):
        """Monitor switch state changes via WebSocket or polling."""
        # This would subscribe to state_changed events via WebSocket
        # For now, we'll use polling as a simple implementation
        while True:
            try:
                for switch_type in self.switches.keys():
                    await self.get_switch_state(switch_type)
                await asyncio.sleep(5)  # Poll every 5 seconds
            except Exception as err:
                _LOGGER.error("[switches] Error monitoring switches: %s", err, exc_info=True)
                await asyncio.sleep(10)
    
    async def close(self):
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

