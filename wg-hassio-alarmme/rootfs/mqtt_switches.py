"""Virtual switches via MQTT Discovery."""
import asyncio
import json
import logging
import os
from typing import Dict, Optional, Callable

try:
    import paho.mqtt.client as mqtt
except ImportError:
    paho = None

_LOGGER = logging.getLogger(__name__)


class MQTTSwitches:
    """Manage virtual switches via MQTT Discovery."""
    
    def __init__(self):
        """Initialize MQTT switches manager."""
        self.mqtt_host = os.environ.get("MQTT_HOST", "core-mosquitto")
        self.mqtt_port = int(os.environ.get("MQTT_PORT", "1883"))
        self.mqtt_user = os.environ.get("MQTT_USER", "")
        self.mqtt_password = os.environ.get("MQTT_PASSWORD", "")
        
        self.switches = {
            "away": {
                "unique_id": "alarmme_away_mode",
                "name": "Away Mode",
                "friendly_name": "Режим отсутствия",
                "icon": "mdi:shield-home",
                "state": "OFF",
                "state_topic": "alarmme/switch/away/state",
                "command_topic": "alarmme/switch/away/set"
            },
            "night": {
                "unique_id": "alarmme_night_mode",
                "name": "Night Mode",
                "friendly_name": "Ночной режим",
                "icon": "mdi:weather-night",
                "state": "OFF",
                "state_topic": "alarmme/switch/night/state",
                "command_topic": "alarmme/switch/night/set"
            }
        }
        
        self.client: Optional[mqtt.Client] = None
        self.state_callback: Optional[Callable[[str, str], None]] = None
        self._connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response from the server."""
        if rc == 0:
            _LOGGER.info("[mqtt_switches] Connected to MQTT broker")
            self._connected = True
            
            # Subscribe to command topics
            for switch_type, switch_data in self.switches.items():
                topic = switch_data["command_topic"]
                client.subscribe(topic)
                _LOGGER.info("[mqtt_switches] Subscribed to command topic: %s", topic)
            
            # Publish discovery messages
            asyncio.create_task(self._publish_discovery())
        else:
            _LOGGER.error("[mqtt_switches] Failed to connect to MQTT broker, return code: %s", rc)
            self._connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the server."""
        _LOGGER.warning("[mqtt_switches] Disconnected from MQTT broker, return code: %s", rc)
        self._connected = False
    
    def _on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received from the server."""
        topic = msg.topic
        payload = msg.payload.decode()
        
        _LOGGER.info("[mqtt_switches] Received message on topic %s: %s", topic, payload)
        
        # Find which switch this command is for
        for switch_type, switch_data in self.switches.items():
            if topic == switch_data["command_topic"]:
                # Update state
                new_state = payload.upper()
                if new_state in ("ON", "OFF"):
                    old_state = switch_data["state"]
                    switch_data["state"] = new_state
                    
                    # Publish state update
                    asyncio.create_task(self._publish_state(switch_type))
                    
                    # Call callback if set
                    if self.state_callback:
                        self.state_callback(switch_type, new_state)
                    
                    _LOGGER.info("[mqtt_switches] Switch %s changed from %s to %s", 
                               switch_data["name"], old_state, new_state)
                break
    
    async def _publish_discovery(self):
        """Publish MQTT Discovery messages."""
        if not self.client or not self._connected:
            return
        
        for switch_type, switch_data in self.switches.items():
            discovery_topic = f"homeassistant/switch/{switch_data['unique_id']}/config"
            
            discovery_payload = {
                "name": switch_data["name"],
                "unique_id": switch_data["unique_id"],
                "state_topic": switch_data["state_topic"],
                "command_topic": switch_data["command_topic"],
                "payload_on": "ON",
                "payload_off": "OFF",
                "state_on": "ON",
                "state_off": "OFF",
                "icon": switch_data["icon"],
                "device": {
                    "identifiers": ["alarmme"],
                    "name": "AlarmMe",
                    "model": "AlarmMe Add-on",
                    "manufacturer": "wargotik"
                }
            }
            
            payload_json = json.dumps(discovery_payload)
            result = self.client.publish(discovery_topic, payload_json, retain=True)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                _LOGGER.info("[mqtt_switches] Published discovery for %s", switch_data["name"])
            else:
                _LOGGER.error("[mqtt_switches] Failed to publish discovery for %s, error: %s", 
                            switch_data["name"], result.rc)
            
            # Small delay between publications
            await asyncio.sleep(0.5)
        
        # Publish initial states
        await asyncio.sleep(1)
        for switch_type in self.switches.keys():
            await self._publish_state(switch_type)
    
    async def _publish_state(self, switch_type: str):
        """Publish switch state to MQTT."""
        if switch_type not in self.switches:
            return
        
        if not self.client or not self._connected:
            return
        
        switch_data = self.switches[switch_type]
        topic = switch_data["state_topic"]
        state = switch_data["state"]
        
        result = self.client.publish(topic, state, retain=True)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            _LOGGER.debug("[mqtt_switches] Published state for %s: %s", switch_data["name"], state)
        else:
            _LOGGER.error("[mqtt_switches] Failed to publish state for %s, error: %s", 
                        switch_data["name"], result.rc)
    
    def start(self):
        """Start MQTT client."""
        if paho is None:
            _LOGGER.error("[mqtt_switches] paho-mqtt not installed. Install it: pip install paho-mqtt")
            return False
        
        try:
            self.client = mqtt.Client(client_id="alarmme_addon")
            
            if self.mqtt_user and self.mqtt_password:
                self.client.username_pw_set(self.mqtt_user, self.mqtt_password)
            
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            _LOGGER.info("[mqtt_switches] Connecting to MQTT broker: %s:%s", self.mqtt_host, self.mqtt_port)
            self.client.connect(self.mqtt_host, self.mqtt_port, 60)
            
            # Start network loop in background thread
            self.client.loop_start()
            
            return True
        except Exception as err:
            _LOGGER.error("[mqtt_switches] Error starting MQTT client: %s", err, exc_info=True)
            return False
    
    def stop(self):
        """Stop MQTT client."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            _LOGGER.info("[mqtt_switches] MQTT client stopped")
    
    def get_switch_state(self, switch_type: str) -> Optional[str]:
        """Get current switch state."""
        if switch_type in self.switches:
            return self.switches[switch_type]["state"]
        return None
    
    def get_all_states(self) -> Dict[str, str]:
        """Get all switch states."""
        return {switch_type: switch_data["state"] for switch_type, switch_data in self.switches.items()}

