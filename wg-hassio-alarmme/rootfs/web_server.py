"""Web server for AlarmMe add-on."""
import asyncio
import aiohttp
from aiohttp import web
import logging
import os
import json

_LOGGER = logging.getLogger(__name__)


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
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-top: 30px;
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
            <p>AlarmMe add-on is running.</p>
            <div class="sensors-grid">
                <div class="sensor-column">
                    <h3>Датчики движения</h3>
                    <div id="motion-sensors" class="loading">Загрузка...</div>
                </div>
                <div class="sensor-column">
                    <h3>Датчики присутствия</h3>
                    <div id="occupancy-sensors" class="loading">Загрузка...</div>
                </div>
            </div>
        </div>
        <script>
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
                        document.getElementById('motion-sensors').innerHTML = 
                            '<div class="empty-state">Ошибка загрузки (статус: ' + response.status + ')</div>';
                        document.getElementById('occupancy-sensors').innerHTML = 
                            '<div class="empty-state">Ошибка загрузки (статус: ' + response.status + ')</div>';
                        return;
                    }
                    
                    const data = await response.json();
                    console.log('Received data:', data);
                    
                    if (data.success) {
                        renderSensors('motion-sensors', data.motion_sensors);
                        renderSensors('occupancy-sensors', data.occupancy_sensors);
                    } else {
                        console.error('API returned success=false:', data.error);
                        document.getElementById('motion-sensors').innerHTML = 
                            '<div class="empty-state">Ошибка: ' + (data.error || 'Неизвестная ошибка') + '</div>';
                        document.getElementById('occupancy-sensors').innerHTML = 
                            '<div class="empty-state">Ошибка: ' + (data.error || 'Неизвестная ошибка') + '</div>';
                    }
                } catch (error) {
                    console.error('Error loading sensors:', error);
                    document.getElementById('motion-sensors').innerHTML = 
                        '<div class="empty-state">Ошибка загрузки: ' + error.message + '</div>';
                    document.getElementById('occupancy-sensors').innerHTML = 
                        '<div class="empty-state">Ошибка загрузки: ' + error.message + '</div>';
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
            
            // Load sensors on page load
            loadSensors();
            
            // Refresh sensors every 5 seconds
            setInterval(loadSensors, 5000);
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
    """Get motion and occupancy sensors from Home Assistant."""
    client_ip = request.remote
    _LOGGER.info("[web_server] Received request to get sensors list from %s", client_ip)
    try:
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        motion_sensors = []
        occupancy_sensors = []
        
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
                                elif device_class == "occupancy":
                                    occupancy_sensors.append({
                                        "entity_id": entity_id,
                                        "name": friendly_name,
                                        "state": state.get("state", "unknown")
                                    })
                                    _LOGGER.debug("[web_server] Found occupancy sensor: %s (%s) - state: %s", 
                                                 friendly_name, entity_id, state.get("state", "unknown"))
                            
                            _LOGGER.info("[web_server] Successfully processed sensors - motion: %d, occupancy: %d", 
                                       len(motion_sensors), len(occupancy_sensors))
                        else:
                            _LOGGER.warning("[web_server] HA API returned status %s, response: %s", 
                                          resp.status, response_text[:200])
            except Exception as api_err:
                _LOGGER.error("[web_server] Error getting sensors from HA API: %s", api_err, exc_info=True)
        else:
            _LOGGER.warning("[web_server] SUPERVISOR_TOKEN not found, cannot fetch sensors")
        
        _LOGGER.info("[web_server] Returning sensors list - motion: %d, occupancy: %d", 
                    len(motion_sensors), len(occupancy_sensors))
        return web.json_response({
            "success": True,
            "motion_sensors": motion_sensors,
            "occupancy_sensors": occupancy_sensors
        })
    except Exception as err:
        _LOGGER.error("[web_server] Error getting sensors: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err),
            "motion_sensors": [],
            "occupancy_sensors": []
        }, status=500)


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
    
    # 404 handler
    app.router.add_route("*", "/{path:.*}", not_found_handler)
    
    _LOGGER.info("[web_server] Registered routes: /, /health, /api/sensors")
    
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

