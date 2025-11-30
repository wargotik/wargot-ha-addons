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
                display: flex;
                height: 100vh;
                overflow: hidden;
            }
            .sidebar {
                width: 300px;
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                overflow-y: auto;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            }
            .sidebar h2 {
                margin-bottom: 20px;
                font-size: 18px;
                border-bottom: 2px solid #34495e;
                padding-bottom: 10px;
            }
            .sensor-column {
                margin-bottom: 30px;
            }
            .sensor-column h3 {
                font-size: 14px;
                text-transform: uppercase;
                margin-bottom: 15px;
                color: #ecf0f1;
                font-weight: 600;
            }
            .sensor-item {
                background-color: #34495e;
                padding: 12px;
                margin-bottom: 8px;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .sensor-item:hover {
                background-color: #3d566e;
            }
            .sensor-item.active {
                background-color: #3498db;
            }
            .sensor-name {
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 4px;
            }
            .sensor-id {
                font-size: 11px;
                color: #bdc3c7;
                font-family: monospace;
            }
            .sensor-state {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 11px;
                margin-top: 6px;
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
            .main-content {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                max-width: 1200px;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
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
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>AlarmMe</h2>
            <div class="sensor-column">
                <h3>Датчики движения</h3>
                <div id="motion-sensors" class="loading">Загрузка...</div>
            </div>
            <div class="sensor-column">
                <h3>Датчики присутствия</h3>
                <div id="occupancy-sensors" class="loading">Загрузка...</div>
            </div>
        </div>
        <div class="main-content">
            <div class="container">
                <h1>AlarmMe</h1>
                <p>AlarmMe add-on is running.</p>
            </div>
        </div>
        <script>
            async function loadSensors() {
                try {
                    const response = await fetch('/api/sensors');
                    const data = await response.json();
                    
                    if (data.success) {
                        renderSensors('motion-sensors', data.motion_sensors);
                        renderSensors('occupancy-sensors', data.occupancy_sensors);
                    } else {
                        document.getElementById('motion-sensors').innerHTML = 
                            '<div class="empty-state">Ошибка загрузки</div>';
                        document.getElementById('occupancy-sensors').innerHTML = 
                            '<div class="empty-state">Ошибка загрузки</div>';
                    }
                } catch (error) {
                    console.error('Error loading sensors:', error);
                    document.getElementById('motion-sensors').innerHTML = 
                        '<div class="empty-state">Ошибка загрузки</div>';
                    document.getElementById('occupancy-sensors').innerHTML = 
                        '<div class="empty-state">Ошибка загрузки</div>';
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


async def get_sensors_handler(request):
    """Get motion and occupancy sensors from Home Assistant."""
    try:
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        motion_sensors = []
        occupancy_sensors = []
        
        if ha_token:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {ha_token}"}
                    api_url = f"{ha_url}/api/states"
                    
                    async with session.get(api_url, headers=headers) as resp:
                        if resp.status == 200:
                            states = await resp.json()
                            
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
                                elif device_class == "occupancy":
                                    occupancy_sensors.append({
                                        "entity_id": entity_id,
                                        "name": friendly_name,
                                        "state": state.get("state", "unknown")
                                    })
                            
                            _LOGGER.info("Found %d motion sensors and %d occupancy sensors", 
                                       len(motion_sensors), len(occupancy_sensors))
                        else:
                            _LOGGER.warning("Failed to get states from HA API: status %s", resp.status)
            except Exception as api_err:
                _LOGGER.error("Error getting sensors from HA API: %s", api_err, exc_info=True)
        else:
            _LOGGER.warning("SUPERVISOR_TOKEN not found, cannot fetch sensors")
        
        return web.json_response({
            "success": True,
            "motion_sensors": motion_sensors,
            "occupancy_sensors": occupancy_sensors
        })
    except Exception as err:
        _LOGGER.error("Error getting sensors: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err),
            "motion_sensors": [],
            "occupancy_sensors": []
        }, status=500)


async def run_web_server(port: int = 8099):
    """Run the web server."""
    app = web.Application()
    
    # Routes
    app.router.add_get("/", index_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/api/sensors", get_sensors_handler)
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    _LOGGER.info(f"Web server started on port {port}")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()

