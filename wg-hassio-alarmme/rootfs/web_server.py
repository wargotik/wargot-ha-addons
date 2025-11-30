"""Web server for AlarmMe add-on."""
import asyncio
import aiohttp
from aiohttp import web
import logging
import os
import json

_LOGGER = logging.getLogger(__name__)

# Global MQTT switches instance
_mqtt_switches = None


def set_mqtt_switches(mqtt_switches):
    """Set MQTT switches instance."""
    global _mqtt_switches
    _mqtt_switches = mqtt_switches


async def index_handler(request):
    """Handle index page."""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AlarmMe</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background-color: #f5f5f5;
                padding: 20px;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            .sensors-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin-top: 30px;
            }
            @media (min-width: 1200px) {
                .sensors-grid {
                    grid-template-columns: repeat(4, 1fr);
                }
            }
            .sensor-column {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
            }
            .sensor-column h3 {
                font-size: 16px;
                color: #333;
                margin-bottom: 15px;
                font-weight: 600;
            }
            .sensor-item {
                background-color: white;
                padding: 12px;
                margin-bottom: 8px;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
                transition: box-shadow 0.2s;
            }
            .sensor-item:hover {
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .sensor-name {
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 4px;
                color: #333;
            }
            .sensor-id {
                font-size: 11px;
                color: #7f8c8d;
                font-family: monospace;
                margin-bottom: 6px;
            }
            .sensor-state {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 600;
            }
            .sensor-state.on {
                background-color: #27ae60;
                color: white;
            }
            .sensor-state.off {
                background-color: #7f8c8d;
                color: white;
            }
            .sensor-state.unknown {
                background-color: #e74c3c;
                color: white;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #7f8c8d;
            }
            .empty-state {
                text-align: center;
                padding: 20px;
                color: #95a5a6;
                font-style: italic;
            }
            .update-badge {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                margin-top: 10px;
                font-weight: 500;
            }
            .mqtt-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                margin-left: 10px;
                font-weight: 500;
            }
            .mqtt-badge.connected {
                background-color: #27ae60;
                color: white;
            }
            .mqtt-badge.disconnected {
                background-color: #e74c3c;
                color: white;
            }
            .mqtt-badge.unknown {
                background-color: #7f8c8d;
                color: white;
            }
            @media (max-width: 768px) {
                .sensors-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AlarmMe</h1>
            <p>AlarmMe add-on is running. 
                <span id="update-badge" class="update-badge">Обновление...</span>
                <span id="mqtt-badge" class="mqtt-badge unknown">MQTT: проверка...</span>
            </p>
            <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                <h3 style="margin-top: 0; margin-bottom: 15px;">Виртуальные выключатели</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                    <div style="padding: 12px; background-color: white; border-radius: 4px; border: 1px solid #e0e0e0;">
                        <div style="font-weight: 600; margin-bottom: 8px;">Away Mode</div>
                        <div style="font-size: 12px; color: #7f8c8d; margin-bottom: 8px;">Режим отсутствия</div>
                        <div style="margin-bottom: 8px;">
                            <div id="switch-away-state" style="display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; background-color: #7f8c8d; color: white; margin-right: 8px;">Загрузка...</div>
                            <span id="switch-away-installed" style="font-size: 11px; color: #7f8c8d;">Проверка...</span>
                        </div>
                    </div>
                    <div style="padding: 12px; background-color: white; border-radius: 4px; border: 1px solid #e0e0e0;">
                        <div style="font-weight: 600; margin-bottom: 8px;">Night Mode</div>
                        <div style="font-size: 12px; color: #7f8c8d; margin-bottom: 8px;">Ночной режим</div>
                        <div style="margin-bottom: 8px;">
                            <div id="switch-night-state" style="display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; background-color: #7f8c8d; color: white; margin-right: 8px;">Загрузка...</div>
                            <span id="switch-night-installed" style="font-size: 11px; color: #7f8c8d;">Проверка...</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="sensors-grid">
                <div class="sensor-column">
                    <h3>Motion<br><small>(PIR движение)</small></h3>
                    <div id="motion-sensors" class="loading">Загрузка...</div>
                </div>
                <div class="sensor-column">
                    <h3>Moving<br><small>(движущийся объект)</small></h3>
                    <div id="moving-sensors" class="loading">Загрузка...</div>
                </div>
                <div class="sensor-column">
                    <h3>Occupancy<br><small>(занятость зоны)</small></h3>
                    <div id="occupancy-sensors" class="loading">Загрузка...</div>
                </div>
                <div class="sensor-column">
                    <h3>Presence<br><small>(статическое присутствие)</small></h3>
                    <div id="presence-sensors" class="loading">Загрузка...</div>
                </div>
            </div>
        </div>
        <script>
            let lastUpdateTime = null;
            
            function updateBadge() {
                const badge = document.getElementById('update-badge');
                if (!badge || !lastUpdateTime) return;
                
                const secondsAgo = Math.floor((Date.now() - lastUpdateTime) / 1000);
                if (secondsAgo < 60) {
                    badge.textContent = secondsAgo + ' секунд назад';
                } else if (secondsAgo < 3600) {
                    const minutesAgo = Math.floor(secondsAgo / 60);
                    badge.textContent = minutesAgo + ' минут назад';
                } else {
                    const hoursAgo = Math.floor(secondsAgo / 3600);
                    badge.textContent = hoursAgo + ' часов назад';
                }
            }
            
            async function loadSensors() {
                try {
                    console.log('Loading sensors...');
                    // Use relative path that works with Ingress
                    const apiPath = window.location.pathname.replace(/\/$/, '') + '/api/sensors';
                    console.log('API path:', apiPath);
                    const response = await fetch(apiPath);
                    console.log('Response status:', response.status);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error('Error response:', response.status, errorText);
                        const errorMsg = '<div class="empty-state">Ошибка загрузки (статус: ' + response.status + ')</div>';
                        document.getElementById('motion-sensors').innerHTML = errorMsg;
                        document.getElementById('moving-sensors').innerHTML = errorMsg;
                        document.getElementById('occupancy-sensors').innerHTML = errorMsg;
                        document.getElementById('presence-sensors').innerHTML = errorMsg;
                        return;
                    }
                    
                    const data = await response.json();
                    console.log('Received data:', data);
                    
                    if (data.success) {
                        renderSensors('motion-sensors', data.motion_sensors || []);
                        renderSensors('moving-sensors', data.moving_sensors || []);
                        renderSensors('occupancy-sensors', data.occupancy_sensors || []);
                        renderSensors('presence-sensors', data.presence_sensors || []);
                        lastUpdateTime = Date.now();
                        updateBadge();
                    } else {
                        console.error('API returned success=false:', data.error);
                        const errorMsg = '<div class="empty-state">Ошибка: ' + (data.error || 'Неизвестная ошибка') + '</div>';
                        document.getElementById('motion-sensors').innerHTML = errorMsg;
                        document.getElementById('moving-sensors').innerHTML = errorMsg;
                        document.getElementById('occupancy-sensors').innerHTML = errorMsg;
                        document.getElementById('presence-sensors').innerHTML = errorMsg;
                    }
                } catch (error) {
                    console.error('Error loading sensors:', error);
                    const errorMsg = '<div class="empty-state">Ошибка загрузки: ' + error.message + '</div>';
                    document.getElementById('motion-sensors').innerHTML = errorMsg;
                    document.getElementById('moving-sensors').innerHTML = errorMsg;
                    document.getElementById('occupancy-sensors').innerHTML = errorMsg;
                    document.getElementById('presence-sensors').innerHTML = errorMsg;
                }
            }
            
            function renderSensors(containerId, sensors) {
                const container = document.getElementById(containerId);
                
                if (sensors.length === 0) {
                    container.innerHTML = '<div class="empty-state">Нет датчиков</div>';
                    return;
                }
                
                container.innerHTML = sensors.map(sensor => {
                    const stateClass = sensor.state === 'on' ? 'on' : 
                                      sensor.state === 'off' ? 'off' : 'unknown';
                    return `
                        <div class="sensor-item">
                            <div class="sensor-name">${sensor.name || sensor.entity_id}</div>
                            <div class="sensor-id">${sensor.entity_id}</div>
                            <div class="sensor-state ${stateClass}">${sensor.state}</div>
                        </div>
                    `;
                }).join('');
            }
            
            async function loadSwitches() {
                try {
                    const apiPath = window.location.pathname.replace(/\/$/, '') + '/api/switches';
                    const response = await fetch(apiPath);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            updateSwitchState('away', data.switches.away || 'OFF');
                            updateSwitchState('night', data.switches.night || 'OFF');
                            updateMqttBadge(data.mqtt_connected !== undefined ? data.mqtt_connected : false);
                            
                            // Update installation status
                            if (data.switches_installed) {
                                updateSwitchInstalled('away', data.switches_installed.away);
                                updateSwitchInstalled('night', data.switches_installed.night);
                            }
                        }
                    }
                } catch (error) {
                    console.error('Error loading switches:', error);
                    updateMqttBadge(false);
                }
            }
            
            function updateSwitchState(switchType, state) {
                const element = document.getElementById('switch-' + switchType + '-state');
                if (!element) return;
                
                const isOn = state === 'ON';
                element.textContent = isOn ? 'ВКЛ' : 'ВЫКЛ';
                element.style.backgroundColor = isOn ? '#27ae60' : '#7f8c8d';
            }
            
            function updateSwitchInstalled(switchType, installed) {
                const element = document.getElementById('switch-' + switchType + '-installed');
                if (!element) return;
                
                if (installed) {
                    element.textContent = '✓ Установлен';
                    element.style.color = '#27ae60';
                } else {
                    element.textContent = '✗ Не установлен';
                    element.style.color = '#e74c3c';
                }
            }
            
            function updateMqttBadge(connected) {
                const badge = document.getElementById('mqtt-badge');
                if (!badge) return;
                
                if (connected) {
                    badge.textContent = 'MQTT: подключен';
                    badge.className = 'mqtt-badge connected';
                } else {
                    badge.textContent = 'MQTT: отключен';
                    badge.className = 'mqtt-badge disconnected';
                }
            }
            
            // Load sensors on page load
            loadSensors();
            loadSwitches();
            
            // Refresh sensors every 30 seconds
            setInterval(loadSensors, 30000);
            
            // Refresh switches every 5 seconds
            setInterval(loadSwitches, 5000);
            
            // Update badge every second
            setInterval(updateBadge, 1000);
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


async def health_handler(request):
    """Handle health check endpoint."""
    return web.json_response({"status": "ok"})


async def send_notification(service_name: str, message: str, title: str = None) -> bool:
    """Send notification via Home Assistant notify service."""
    try:
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        if not ha_token:
            _LOGGER.warning("[web_server] SUPERVISOR_TOKEN not found, cannot send notification")
            return False
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {ha_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare notification data
            notification_data = {"message": message}
            if title:
                notification_data["title"] = title
            
            # Call notify service
            api_url = f"{ha_url}/api/services/notify/{service_name}"
            _LOGGER.info("[web_server] Sending notification via %s: %s", service_name, message)
            
            async with session.post(api_url, headers=headers, json=notification_data) as resp:
                if resp.status == 200:
                    _LOGGER.info("[web_server] Notification sent successfully via %s", service_name)
                    return True
                else:
                    response_text = await resp.text()
                    _LOGGER.warning("[web_server] Failed to send notification via %s: status %s, response: %s", 
                                  service_name, resp.status, response_text[:200])
                    return False
    except Exception as err:
        _LOGGER.error("[web_server] Error sending notification via %s: %s", service_name, err, exc_info=True)
        return False


async def get_sensors_handler(request):
    """Get motion, moving, occupancy and presence sensors from Home Assistant."""
    client_ip = request.remote
    _LOGGER.info("[web_server] Received request to get sensors list from %s", client_ip)
    try:
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        motion_sensors = []
        moving_sensors = []
        occupancy_sensors = []
        presence_sensors = []
        
        if ha_token:
            _LOGGER.debug("[web_server] SUPERVISOR_TOKEN found, requesting sensors from HA API: %s", ha_url)
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {ha_token}"}
                    api_url = f"{ha_url}/api/states"
                    
                    _LOGGER.debug("[web_server] Making request to HA API: %s", api_url)
                    async with session.get(api_url, headers=headers) as resp:
                        response_text = await resp.text()
                        _LOGGER.debug("[web_server] HA API response status: %s", resp.status)
                        
                        if resp.status == 200:
                            try:
                                states = await resp.json()
                                total_states = len(states)
                                _LOGGER.info("[web_server] Received %d total states from HA API", total_states)
                            except Exception as json_err:
                                _LOGGER.error("[web_server] Error parsing JSON response from HA API: %s, response: %s", 
                                            json_err, response_text[:500])
                                raise
                            
                            for state in states:
                                entity_id = state.get("entity_id", "")
                                attributes = state.get("attributes", {})
                                device_class = attributes.get("device_class", "")
                                friendly_name = attributes.get("friendly_name", entity_id)
                                
                                if device_class == "motion":
                                    motion_sensors.append({
                                        "entity_id": entity_id,
                                        "name": friendly_name,
                                        "state": state.get("state", "unknown")
                                    })
                                    _LOGGER.debug("[web_server] Found motion sensor: %s (%s) - state: %s", 
                                                 friendly_name, entity_id, state.get("state", "unknown"))
                                elif device_class == "moving":
                                    moving_sensors.append({
                                        "entity_id": entity_id,
                                        "name": friendly_name,
                                        "state": state.get("state", "unknown")
                                    })
                                    _LOGGER.debug("[web_server] Found moving sensor: %s (%s) - state: %s", 
                                                 friendly_name, entity_id, state.get("state", "unknown"))
                                elif device_class == "occupancy":
                                    occupancy_sensors.append({
                                        "entity_id": entity_id,
                                        "name": friendly_name,
                                        "state": state.get("state", "unknown")
                                    })
                                    _LOGGER.debug("[web_server] Found occupancy sensor: %s (%s) - state: %s", 
                                                 friendly_name, entity_id, state.get("state", "unknown"))
                                elif device_class == "presence":
                                    presence_sensors.append({
                                        "entity_id": entity_id,
                                        "name": friendly_name,
                                        "state": state.get("state", "unknown")
                                    })
                                    _LOGGER.debug("[web_server] Found presence sensor: %s (%s) - state: %s", 
                                                 friendly_name, entity_id, state.get("state", "unknown"))
                            
                            _LOGGER.info("[web_server] Successfully processed sensors - motion: %d, moving: %d, occupancy: %d, presence: %d", 
                                       len(motion_sensors), len(moving_sensors), len(occupancy_sensors), len(presence_sensors))
                        else:
                            _LOGGER.warning("[web_server] HA API returned status %s, response: %s", 
                                          resp.status, response_text[:200])
            except Exception as api_err:
                _LOGGER.error("[web_server] Error getting sensors from HA API: %s", api_err, exc_info=True)
        else:
            _LOGGER.warning("[web_server] SUPERVISOR_TOKEN not found, cannot fetch sensors")
        
        _LOGGER.info("[web_server] Returning sensors list - motion: %d, moving: %d, occupancy: %d, presence: %d", 
                    len(motion_sensors), len(moving_sensors), len(occupancy_sensors), len(presence_sensors))
        return web.json_response({
            "success": True,
            "motion_sensors": motion_sensors,
            "moving_sensors": moving_sensors,
            "occupancy_sensors": occupancy_sensors,
            "presence_sensors": presence_sensors
        })
    except Exception as err:
        _LOGGER.error("[web_server] Error getting sensors: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err),
            "motion_sensors": [],
            "moving_sensors": [],
            "occupancy_sensors": [],
            "presence_sensors": []
        }, status=500)


async def _check_switch_exists(entity_id: str) -> bool:
    """Check if switch entity exists in Home Assistant."""
    try:
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        if not ha_token:
            return False
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {ha_token}"}
            api_url = f"{ha_url}/api/states/{entity_id}"
            
            async with session.get(api_url, headers=headers) as resp:
                return resp.status == 200
    except Exception as err:
        _LOGGER.debug("[web_server] Error checking switch existence %s: %s", entity_id, err)
        return False


async def get_switches_handler(request):
    """Get virtual switches state."""
    try:
        global _mqtt_switches
        
        # Default states if MQTT not available
        default_states = {"away": "OFF", "night": "OFF"}
        
        # Check if switches exist in Home Assistant
        away_exists = await _check_switch_exists("switch.alarmme_away_mode")
        night_exists = await _check_switch_exists("switch.alarmme_night_mode")
        
        if _mqtt_switches is None:
            _LOGGER.debug("[web_server] MQTT switches not initialized, returning default states")
            return web.json_response({
                "success": True,
                "switches": default_states,
                "mqtt_connected": False,
                "switches_installed": {
                    "away": away_exists,
                    "night": night_exists
                }
            })
        
        states = _mqtt_switches.get_all_states()
        
        return web.json_response({
            "success": True,
            "switches": {
                "away": states.get("away", "OFF"),
                "night": states.get("night", "OFF")
            },
            "mqtt_connected": _mqtt_switches._connected if hasattr(_mqtt_switches, '_connected') else False,
            "switches_installed": {
                "away": away_exists,
                "night": night_exists
            }
        })
    except Exception as err:
        _LOGGER.error("[web_server] Error getting switches: %s", err, exc_info=True)
        return web.json_response({
            "success": True,
            "error": str(err),
            "switches": {"away": "OFF", "night": "OFF"},
            "mqtt_connected": False,
            "switches_installed": {
                "away": False,
                "night": False
            }
        })


@web.middleware
async def logging_middleware(request, handler):
    """Middleware to log all requests."""
    _LOGGER.info("[web_server] %s %s from %s", request.method, request.path_qs, request.remote)
    try:
        response = await handler(request)
        _LOGGER.info("[web_server] %s %s - status: %s", request.method, request.path_qs, response.status)
        return response
    except web.HTTPNotFound:
        _LOGGER.warning("[web_server] 404 Not Found: %s %s", request.method, request.path_qs)
        raise
    except Exception as err:
        _LOGGER.error("[web_server] Error handling %s %s: %s", request.method, request.path_qs, err, exc_info=True)
        raise


async def not_found_handler(request):
    """Handle 404 errors."""
    _LOGGER.warning("[web_server] 404 Not Found: %s %s", request.method, request.path_qs)
    return web.json_response({
        "success": False,
        "error": f"Route not found: {request.path_qs}"
    }, status=404)


async def run_web_server(port: int = 8099):
    """Run the web server."""
    app = web.Application(middlewares=[logging_middleware])
    
    # Routes
    app.router.add_get("/", index_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/api/sensors", get_sensors_handler)
    app.router.add_get("/api/switches", get_switches_handler)
    
    # 404 handler
    app.router.add_route("*", "/{path:.*}", not_found_handler)
    
    _LOGGER.info("[web_server] Registered routes: /, /health, /api/sensors, /api/switches")
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    _LOGGER.info(f"[web_server] Web server started on port {port}")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()

