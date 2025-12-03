"""Web server for AlarmMe add-on."""
import asyncio
import aiohttp
from aiohttp import web
import logging
import os
import json

from database import SensorDatabase
from sensor_monitor import SensorMonitor

_LOGGER = logging.getLogger(__name__)

# Global virtual switches instance
_virtual_switches = None

# Global database instance
_db = SensorDatabase()

# Global sensor states cache for tracking changes
_sensor_states_cache = {}

# Global sensor monitor instance
_sensor_monitor = None


def set_virtual_switches(virtual_switches):
    """Set virtual switches instance."""
    global _virtual_switches
    _virtual_switches = virtual_switches


def set_sensor_monitor(sensor_monitor):
    """Set sensor monitor instance."""
    global _sensor_monitor
    _sensor_monitor = sensor_monitor


def get_db():
    """Get database instance."""
    return _db


def get_sensor_states_cache():
    """Get sensor states cache."""
    return _sensor_states_cache


async def index_handler(request):
    """Handle index page."""
    # Read version from config.json
    version = "unknown"
    try:
        # Try multiple possible paths for config.json
        possible_paths = [
            "/config.json",  # Standard add-on config location
            "/data/options.json",  # Add-on options (usually doesn't have version)
            os.path.join(os.path.dirname(__file__), "..", "..", "config.json"),  # Relative to script
            "/app/config.json",  # If config is copied to /app
        ]
        
        for config_path in possible_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if "version" in config:
                            version = config.get("version", "unknown")
                            _LOGGER.debug("[web_server] Read version %s from %s", version, config_path)
                            break
                except Exception as path_err:
                    _LOGGER.debug("[web_server] Error reading %s: %s", config_path, path_err)
                    continue
        
        # Fallback: try environment variable
        if version == "unknown":
            version = os.environ.get("ADDON_VERSION", os.environ.get("VERSION", "unknown"))
    except Exception as err:
        _LOGGER.debug("[web_server] Could not read version: %s", err)
        version = os.environ.get("ADDON_VERSION", "unknown")
    
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
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .version-badge {
                display: inline-block;
                background-color: #95a5a6;
                color: white;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 500;
                font-family: monospace;
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
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .sensor-save-icon, .sensor-saved-icon {
                font-size: 16px;
                cursor: pointer;
                opacity: 0.6;
                transition: opacity 0.2s;
            }
            .sensor-save-icon:hover {
                opacity: 1;
            }
            .sensor-saved-icon {
                opacity: 1;
                cursor: default;
            }
            .sensor-id {
                font-size: 11px;
                color: #7f8c8d;
                font-family: monospace;
                margin-bottom: 6px;
            }
            .sensor-modes {
                display: flex;
                gap: 6px;
                margin-top: 8px;
                flex-wrap: wrap;
            }
            .sensor-mode-btn {
                padding: 4px 10px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                color: #333;
                font-size: 11px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            }
            .sensor-mode-btn:hover {
                border-color: #3498db;
                background-color: #f0f8ff;
            }
            .sensor-mode-btn.active {
                border-color: #3498db;
                background-color: #3498db;
                color: white;
            }
            .sensor-mode-btn.active.away {
                border-color: #3498db;
                background-color: #3498db;
            }
            .sensor-mode-btn.active.night {
                border-color: #9b59b6;
                background-color: #9b59b6;
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
            .sensor-last-triggered {
                font-size: 10px;
                color: #7f8c8d;
                margin-top: 4px;
                font-style: italic;
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
            .connection-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                margin-left: 10px;
                font-weight: 500;
            }
            .connection-badge.connected {
                background-color: #27ae60;
                color: white;
            }
            .connection-badge.disconnected {
                background-color: #e74c3c;
                color: white;
            }
            .connection-badge.unknown {
                background-color: #7f8c8d;
                color: white;
            }
            .mode-buttons {
                display: flex;
                gap: 10px;
                margin-top: 15px;
                flex-wrap: wrap;
            }
            .mode-button {
                flex: 1;
                min-width: 120px;
                padding: 12px 20px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                color: #333;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                text-align: center;
            }
            .mode-button:hover {
                border-color: #3498db;
                background-color: #f0f8ff;
            }
            .mode-button.active {
                border-color: #3498db;
                background-color: #3498db;
                color: white;
            }
            .mode-button.active.off {
                border-color: #7f8c8d;
                background-color: #7f8c8d;
            }
            .mode-button.active.away {
                border-color: #3498db;
                background-color: #3498db;
            }
            .mode-button.active.night {
                border-color: #9b59b6;
                background-color: #9b59b6;
            }
            .mode-button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            @media (max-width: 768px) {
                .sensors-grid {
                    grid-template-columns: 1fr;
                }
                .mode-buttons {
                    flex-direction: column;
                }
                .mode-button {
                    width: 100%;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AlarmMe<span class="version-badge">v{version}</span></h1>
            <p>AlarmMe add-on is running. 
                <span id="connection-badge" class="connection-badge unknown">REST API: проверка...</span>
                <span id="background-poll-badge" class="update-badge" style="margin-left: 10px;">Фоновое обновление: проверка...</span>
            </p>
            <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                <div style="padding: 15px; background-color: white; border-radius: 4px; border: 1px solid #e0e0e0;">
                    <div style="margin-bottom: 12px;">
                        <div style="font-weight: 600; margin-bottom: 8px;">Текущий режим</div>
                        <div id="current-mode" style="display: inline-block; padding: 8px 16px; border-radius: 12px; font-size: 14px; font-weight: 600; background-color: #7f8c8d; color: white; margin-right: 8px;">Загрузка...</div>
                        <span id="switches-installed" style="font-size: 11px; color: #7f8c8d;">Проверка...</span>
                    </div>
                    <div class="mode-buttons">
                        <button class="mode-button off" id="mode-button-off" onclick="setMode('off')">
                            Выключено
                        </button>
                        <button class="mode-button away" id="mode-button-away" onclick="setMode('away')">
                            Away Mode
                        </button>
                        <button class="mode-button night" id="mode-button-night" onclick="setMode('night')">
                            Night Mode
                        </button>
                    </div>
                    <div style="font-size: 12px; color: #7f8c8d; margin-top: 12px;">
                        <div>• <strong>Выключено</strong> - оба режима отключены</div>
                        <div>• <strong>Away Mode</strong> - режим отсутствия</div>
                        <div>• <strong>Night Mode</strong> - ночной режим</div>
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
                    // All sensors are auto-saved, so always show saved icon
                    const savedIcon = '<span class="sensor-saved-icon" title="Сохранён в базу">💾</span>';
                    
                    // Mode buttons - ensure boolean values
                    const awayEnabled = Boolean(sensor.enabled_in_away_mode);
                    const nightEnabled = Boolean(sensor.enabled_in_night_mode);
                    const awayModeActive = awayEnabled ? 'active' : '';
                    const nightModeActive = nightEnabled ? 'active' : '';
                    
                    const modeButtons = `
                        <div class="sensor-modes">
                            <button class="sensor-mode-btn away ${awayModeActive}" 
                                    data-entity-id="${sensor.entity_id.replace(/"/g, '&quot;')}"
                                    data-mode="away"
                                    data-enabled="${!awayEnabled}"
                                    title="Включён в Away Mode">
                                Away
                            </button>
                            <button class="sensor-mode-btn night ${nightModeActive}" 
                                    data-entity-id="${sensor.entity_id.replace(/"/g, '&quot;')}"
                                    data-mode="night"
                                    data-enabled="${!nightEnabled}"
                                    title="Включён в Night Mode">
                                Night
                            </button>
                        </div>
                    `;
                    
                    // Format last triggered time
                    let lastTriggeredHtml = '';
                    if (sensor.last_triggered_at) {
                        try {
                            const triggerDate = new Date(sensor.last_triggered_at);
                            const hours = String(triggerDate.getHours()).padStart(2, '0');
                            const minutes = String(triggerDate.getMinutes()).padStart(2, '0');
                            const seconds = String(triggerDate.getSeconds()).padStart(2, '0');
                            const day = String(triggerDate.getDate()).padStart(2, '0');
                            const month = String(triggerDate.getMonth() + 1).padStart(2, '0');
                            const year = triggerDate.getFullYear();
                            const timeStr = hours + ':' + minutes + ':' + seconds;
                            const dateStr = day + '.' + month + '.' + year;
                            
                            lastTriggeredHtml = `<div class="sensor-last-triggered">Последнее срабатывание: ${dateStr} ${timeStr}</div>`;
                        } catch (e) {
                            // If date parsing fails, show raw value
                            lastTriggeredHtml = `<div class="sensor-last-triggered">Последнее срабатывание: ${sensor.last_triggered_at}</div>`;
                        }
                    } else {
                        lastTriggeredHtml = '<div class="sensor-last-triggered">Срабатываний не было</div>';
                    }
                    
                    return `
                        <div class="sensor-item">
                            <div class="sensor-name">
                                ${sensor.name || sensor.entity_id}
                                ${savedIcon}
                            </div>
                            <div class="sensor-id">${sensor.entity_id}</div>
                            <div class="sensor-state ${stateClass}">${sensor.state}</div>
                            ${lastTriggeredHtml}
                            ${modeButtons}
                        </div>
                    `;
                }).join('');
            }
            
            async function saveSensor(entityId, name, deviceClass) {
                try {
                    const apiPath = window.location.pathname.replace(/\/$/, '') + '/api/sensors/save';
                    const response = await fetch(apiPath, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            entity_id: entityId,
                            name: name,
                            device_class: deviceClass
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            // Reload sensors to update UI
                            await loadSensors();
                        } else {
                            alert('Ошибка: ' + (data.error || 'Не удалось сохранить датчик'));
                        }
                    } else {
                        const errorData = await response.json().catch(() => ({ error: 'Ошибка сервера' }));
                        alert('Ошибка: ' + (errorData.error || 'Не удалось сохранить датчик'));
                    }
                } catch (error) {
                    console.error('Error saving sensor:', error);
                    alert('Ошибка: ' + error.message);
                }
            }
            
            async function toggleSensorMode(entityId, mode, enabled) {
                try {
                    console.log('toggleSensorMode:', entityId, mode, enabled);
                    const apiPath = window.location.pathname.replace(/\/$/, '') + '/api/sensors/update-modes';
                    const requestData = {
                        entity_id: entityId
                    };
                    
                    if (mode === 'away') {
                        requestData.enabled_in_away_mode = enabled;
                    } else if (mode === 'night') {
                        requestData.enabled_in_night_mode = enabled;
                    }
                    
                    console.log('Sending request:', requestData);
                    const response = await fetch(apiPath, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(requestData)
                    });
                    
                    console.log('Response status:', response.status);
                    const data = await response.json();
                    console.log('Response data:', data);
                    
                    if (response.ok && data.success) {
                        // Reload sensors to update UI
                        await loadSensors();
                    } else {
                        alert('Ошибка: ' + (data.error || 'Не удалось обновить режим датчика'));
                    }
                } catch (error) {
                    console.error('Error toggling sensor mode:', error);
                    alert('Ошибка: ' + error.message);
                }
            }
            
            async function loadSwitches() {
                try {
                    const apiPath = window.location.pathname.replace(/\/$/, '') + '/api/switches';
                    const response = await fetch(apiPath);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            updateCurrentMode(data.mode || 'off');
                            updateConnectionBadge(data.connected !== undefined ? data.connected : false);
                            
                            // Update installation status (both switches should be installed)
                            if (data.switches_installed) {
                                const bothInstalled = data.switches_installed.away && data.switches_installed.night;
                                updateSwitchesInstalled(bothInstalled);
                            }
                        }
                    }
                } catch (error) {
                    console.error('Error loading switches:', error);
                    updateConnectionBadge(false);
                    updateCurrentMode('off');
                }
            }
            
            function updateCurrentMode(mode) {
                const element = document.getElementById('current-mode');
                if (!element) return;
                
                const modeLabels = {
                    'off': 'Выключено',
                    'away': 'Away Mode',
                    'night': 'Night Mode'
                };
                
                const modeColors = {
                    'off': '#7f8c8d',
                    'away': '#3498db',
                    'night': '#9b59b6'
                };
                
                const label = modeLabels[mode] || 'Неизвестно';
                const color = modeColors[mode] || '#7f8c8d';
                
                element.textContent = label;
                element.style.backgroundColor = color;
                
                // Update button states
                updateModeButtons(mode);
            }
            
            function updateModeButtons(activeMode) {
                const buttons = {
                    'off': document.getElementById('mode-button-off'),
                    'away': document.getElementById('mode-button-away'),
                    'night': document.getElementById('mode-button-night')
                };
                
                for (const [mode, button] of Object.entries(buttons)) {
                    if (button) {
                        if (mode === activeMode) {
                            button.classList.add('active');
                            button.disabled = false;
                        } else {
                            button.classList.remove('active');
                            button.disabled = false;
                        }
                    }
                }
            }
            
            async function setMode(mode) {
                // Disable all buttons during update
                const buttons = ['off', 'away', 'night'].map(m => document.getElementById('mode-button-' + m));
                buttons.forEach(btn => {
                    if (btn) btn.disabled = true;
                });
                
                try {
                    const apiPath = window.location.pathname.replace(/\/$/, '') + '/api/switches';
                    const response = await fetch(apiPath, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ mode: mode })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            // Update UI immediately
                            updateCurrentMode(data.mode || mode);
                            // Reload switches to get latest state
                            await loadSwitches();
                        } else {
                            alert('Ошибка: ' + (data.error || 'Не удалось изменить режим'));
                            // Reload to restore correct state
                            await loadSwitches();
                        }
                    } else {
                        const errorData = await response.json().catch(() => ({ error: 'Ошибка сервера' }));
                        alert('Ошибка: ' + (errorData.error || 'Не удалось изменить режим'));
                        // Reload to restore correct state
                        await loadSwitches();
                    }
                } catch (error) {
                    console.error('Error setting mode:', error);
                    alert('Ошибка: ' + error.message);
                    // Reload to restore correct state
                    await loadSwitches();
                } finally {
                    // Re-enable buttons
                    buttons.forEach(btn => {
                        if (btn) btn.disabled = false;
                    });
                }
            }
            
            function updateSwitchesInstalled(installed) {
                const element = document.getElementById('switches-installed');
                if (!element) return;
                
                if (installed) {
                    element.textContent = '✓ Выключатели установлены';
                    element.style.color = '#27ae60';
                } else {
                    element.textContent = '✗ Выключатели не установлены';
                    element.style.color = '#e74c3c';
                }
            }
            
            function updateConnectionBadge(connected) {
                const badge = document.getElementById('connection-badge');
                if (!badge) return;
                
                if (connected) {
                    badge.textContent = 'REST API: подключен';
                    badge.className = 'connection-badge connected';
                } else {
                    badge.textContent = 'REST API: отключен';
                    badge.className = 'connection-badge disconnected';
                }
            }
            
            async function loadBackgroundPollTime() {
                try {
                    const apiPath = window.location.pathname.replace(/\/$/, '') + '/api/background-poll-time';
                    const response = await fetch(apiPath);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success && data.last_poll_time) {
                            updateBackgroundPollBadge(data.last_poll_time);
                        } else {
                            updateBackgroundPollBadge(null);
                        }
                    }
                } catch (error) {
                    console.error('Error loading background poll time:', error);
                    updateBackgroundPollBadge(null);
                }
            }
            
            function updateBackgroundPollBadge(lastPollTime) {
                const badge = document.getElementById('background-poll-badge');
                if (!badge) return;
                
                if (!lastPollTime) {
                    badge.textContent = 'Фоновое обновление: нет данных';
                    return;
                }
                
                try {
                    const pollDate = new Date(lastPollTime);
                    const now = new Date();
                    const diffMs = now - pollDate;
                    const diffSec = Math.floor(diffMs / 1000);
                    const diffMin = Math.floor(diffSec / 60);
                    const diffHour = Math.floor(diffMin / 60);
                    
                    let timeAgo = '';
                    if (diffSec < 60) {
                        timeAgo = diffSec + ' сек назад';
                    } else if (diffMin < 60) {
                        timeAgo = diffMin + ' мин назад';
                    } else {
                        timeAgo = diffHour + ' ч назад';
                    }
                    
                    // Format time as HH:MM:SS
                    const hours = String(pollDate.getHours()).padStart(2, '0');
                    const minutes = String(pollDate.getMinutes()).padStart(2, '0');
                    const seconds = String(pollDate.getSeconds()).padStart(2, '0');
                    const timeStr = hours + ':' + minutes + ':' + seconds;
                    
                    badge.textContent = 'Фоновое обновление: ' + timeAgo + ' в ' + timeStr;
                } catch (e) {
                    badge.textContent = 'Фоновое обновление: ошибка';
                }
            }
            
            // Event delegation for sensor mode buttons
            document.addEventListener('click', function(event) {
                if (event.target.classList.contains('sensor-mode-btn')) {
                    const entityId = event.target.getAttribute('data-entity-id');
                    const mode = event.target.getAttribute('data-mode');
                    const enabled = event.target.getAttribute('data-enabled') === 'true';
                    if (entityId && mode) {
                        toggleSensorMode(entityId, mode, enabled);
                    }
                }
            });
            
            // Load sensors on page load
            loadSensors();
            loadSwitches();
            loadBackgroundPollTime();
            
            // Refresh sensors every 30 seconds
            setInterval(loadSensors, 30000);
            
            // Refresh switches every 5 seconds
            setInterval(loadSwitches, 5000);
            
            // Refresh background poll time every 5 seconds
            setInterval(loadBackgroundPollTime, 5000);
            
            // Update badge every second
            setInterval(updateBadge, 1000);
        </script>
    </body>
    </html>
    """
    # Replace version placeholder
    html = html.replace("{version}", version)
    return web.Response(text=html, content_type="text/html")


async def health_handler(request):
    """Handle health check endpoint."""
    return web.json_response({"status": "ok"})


async def get_available_notify_services() -> dict:
    """Get list of available notify services from Home Assistant."""
    try:
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        if not ha_token:
            _LOGGER.warning("[web_server] SUPERVISOR_TOKEN not found, cannot get notify services")
            return {"iphone": [], "android": [], "other": [], "all_mobile": []}
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {ha_token}"}
            api_url = f"{ha_url}/api/services"
            _LOGGER.debug("[web_server] Fetching services from: %s", api_url)
            
            async with session.get(api_url, headers=headers) as resp:
                if resp.status == 200:
                    services = await resp.json()
                    _LOGGER.debug("[web_server] Received services response, keys: %s", list(services.keys()) if isinstance(services, dict) else "Not a dict")
                    
                    notify_services = services.get("notify", {})
                    _LOGGER.info("[web_server] All notify services found: %s", list(notify_services.keys()) if notify_services else "None")
                    
                    iphone_services = []
                    android_services = []
                    other_services = []
                    
                    for service_name in notify_services.keys():
                        service_lower = service_name.lower()
                        if "iphone" in service_lower or "ios" in service_lower:
                            iphone_services.append(service_name)
                        elif "android" in service_lower:
                            android_services.append(service_name)
                        elif service_name.startswith("mobile_app_"):
                            other_services.append(service_name)
                    
                    result = {
                        "iphone": iphone_services,
                        "android": android_services,
                        "other": other_services,
                        "all_mobile": iphone_services + android_services + other_services
                    }
                    
                    _LOGGER.info("[web_server] Found notify services: iPhone=%d (%s), Android=%d (%s), Other=%d (%s), Total mobile=%d", 
                               len(iphone_services), iphone_services,
                               len(android_services), android_services,
                               len(other_services), other_services,
                               len(result["all_mobile"]))
                    return result
                else:
                    response_text = await resp.text()
                    _LOGGER.error("[web_server] Failed to get notify services: status %s, response: %s", resp.status, response_text[:500])
                    return {"iphone": [], "android": [], "other": [], "all_mobile": []}
    except Exception as err:
        _LOGGER.error("[web_server] Error getting notify services: %s", err, exc_info=True)
        return {"iphone": [], "android": [], "other": [], "all_mobile": []}


async def send_notification(message: str, persistent_notification: bool = False, title: str = None, actions: list = None) -> bool:
    """Send notification to all available mobile devices (iPhone/Android) and optionally as persistent notification.
    
    Args:
        message: Notification message text
        persistent_notification: If True, also send as persistent notification in HA UI
        title: Optional notification title
        actions: Optional list of action buttons for actionable notifications (mobile devices only)
                 Format: [{"action": "ACTION_ID", "title": "Button Text"}, ...]
    """
    try:
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        if not ha_token:
            _LOGGER.warning("[web_server] SUPERVISOR_TOKEN not found, cannot send notification")
            return False
        
        # Prepare notification data
        notification_data = {"message": message}
        if title:
            notification_data["title"] = title
        
        # Add actions for mobile devices (not for persistent_notification)
        if actions:
            notification_data["data"] = {"actions": actions}
        
        # Get list of available mobile devices
        services = await get_available_notify_services()
        all_mobile_services = services.get("all_mobile", [])
        _LOGGER.info("[web_server] Available mobile services: %s", all_mobile_services)
        
        # Add persistent_notification if requested
        services_to_notify = list(all_mobile_services)
        if persistent_notification:
            services_to_notify.append("persistent_notification")
        
        _LOGGER.info("[web_server] Sending notification to %d services: %s", len(services_to_notify), services_to_notify)
        
        if not services_to_notify:
            _LOGGER.warning("[web_server] No notification services available - cannot send notification")
            return False
        
        # Send notification to all services
        success_count = 0
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {ha_token}",
                "Content-Type": "application/json"
            }
            
            for service_name in services_to_notify:
                try:
                    api_url = f"{ha_url}/api/services/notify/{service_name}"
                    
                    # For persistent_notification, don't send actions (not supported)
                    if service_name == "persistent_notification":
                        persistent_data = {"message": message}
                        if title:
                            persistent_data["title"] = title
                        _LOGGER.debug("[web_server] Sending persistent notification: %s", message)
                        async with session.post(api_url, headers=headers, json=persistent_data) as resp:
                            if resp.status == 200:
                                success_count += 1
                                _LOGGER.info("[web_server] Persistent notification sent successfully")
                            else:
                                response_text = await resp.text()
                                _LOGGER.warning("[web_server] Failed to send persistent notification: status %s, response: %s", 
                                              resp.status, response_text[:200])
                    else:
                        # For mobile devices, send with actions if provided
                        _LOGGER.info("[web_server] Sending notification via %s: %s (actions: %s, data: %s)", 
                                     service_name, message, actions, notification_data)
                        async with session.post(api_url, headers=headers, json=notification_data) as resp:
                            response_text = await resp.text()
                            if resp.status == 200:
                                success_count += 1
                                _LOGGER.info("[web_server] Notification sent successfully via %s, response: %s", 
                                           service_name, response_text[:200])
                            else:
                                _LOGGER.error("[web_server] Failed to send notification via %s: status %s, response: %s", 
                                              service_name, resp.status, response_text[:500])
                except Exception as service_err:
                    _LOGGER.error("[web_server] Error sending notification via %s: %s", service_name, service_err)
        
        if success_count > 0:
            _LOGGER.info("[web_server] Notification sent to %d/%d services", success_count, len(services_to_notify))
            return True
        else:
            _LOGGER.warning("[web_server] Failed to send notification to any service")
            return False
            
    except Exception as err:
        _LOGGER.error("[web_server] Error sending notification: %s", err, exc_info=True)
        return False


async def get_sensors_handler(request):
    """Get sensors from database and their current states from Home Assistant (read-only, no saving/triggers)."""
    client_ip = request.remote
    _LOGGER.info("[web_server] Received UI request to get sensors list from %s", client_ip)
    try:
        global _db
        
        # Get all sensors from database (only saved sensors)
        saved_sensors = _db.get_all_sensors()
        _LOGGER.info("[web_server] Found %d sensors in database", len(saved_sensors))
        
        # Create a map of entity_id -> sensor data from database
        sensors_by_id = {s["entity_id"]: s for s in saved_sensors}
        
        # Get current states from HA API (only for display, no saving/triggers)
        ha_states_map = {}
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        if ha_token and sensors_by_id:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {ha_token}"}
                    api_url = f"{ha_url}/api/states"
                    
                    _LOGGER.debug("[web_server] Fetching current states from HA API for %d sensors (display only)", len(sensors_by_id))
                    async with session.get(api_url, headers=headers) as resp:
                        if resp.status == 200:
                            states = await resp.json()
                            # Create map of entity_id -> state for quick lookup
                            for state in states:
                                entity_id = state.get("entity_id", "")
                                if entity_id in sensors_by_id:
                                    ha_states_map[entity_id] = state.get("state", "unknown")
                            _LOGGER.debug("[web_server] Retrieved current states for %d sensors", len(ha_states_map))
                        else:
                            _LOGGER.warning("[web_server] HA API returned status %s, will show sensors without current state", resp.status)
            except Exception as api_err:
                _LOGGER.warning("[web_server] Error fetching current states from HA API: %s (will show sensors without current state)", api_err)
        
        # Build sensor lists grouped by device_class
        motion_sensors = []
        moving_sensors = []
        occupancy_sensors = []
        presence_sensors = []
        
        for saved_sensor in saved_sensors:
            entity_id = saved_sensor["entity_id"]
            device_class = saved_sensor["device_class"]
            
            # Get current state from HA (or "unknown" if not available)
            current_state = ha_states_map.get(entity_id, "unknown")
            
            sensor_data = {
                "entity_id": entity_id,
                "name": saved_sensor["name"],
                "state": current_state,
                "device_class": device_class,
                "saved": True,  # All sensors from database are saved
                "enabled_in_away_mode": bool(saved_sensor.get("enabled_in_away_mode", False)),
                "enabled_in_night_mode": bool(saved_sensor.get("enabled_in_night_mode", False)),
                "last_triggered_at": saved_sensor.get("last_triggered_at")
            }
            
            # Group by device_class
            if device_class == "motion":
                motion_sensors.append(sensor_data)
            elif device_class == "moving":
                moving_sensors.append(sensor_data)
            elif device_class == "occupancy":
                occupancy_sensors.append(sensor_data)
            elif device_class == "presence":
                presence_sensors.append(sensor_data)
        
        _LOGGER.info("[web_server] Returning sensors from database - motion: %d, moving: %d, occupancy: %d, presence: %d", 
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


async def save_sensor_handler(request):
    """Save sensor to database (POST)."""
    try:
        global _db
        
        # Parse request body
        try:
            data = await request.json()
        except Exception as json_err:
            _LOGGER.warning("[web_server] Invalid JSON in request: %s", json_err)
            return web.json_response({
                "success": False,
                "error": "Invalid JSON"
            }, status=400)
        
        entity_id = data.get("entity_id")
        name = data.get("name", "")
        device_class = data.get("device_class", "")
        
        if not entity_id:
            return web.json_response({
                "success": False,
                "error": "entity_id is required"
            }, status=400)
        
        _LOGGER.info("[web_server] Saving sensor to database: %s (%s)", name, entity_id)
        
        success = _db.save_sensor(
            entity_id=entity_id,
            name=name,
            device_class=device_class,
            enabled_in_away_mode=False,
            enabled_in_night_mode=False
        )
        
        if success:
            return web.json_response({
                "success": True,
                "message": "Sensor saved successfully"
            })
        else:
            return web.json_response({
                "success": False,
                "error": "Failed to save sensor"
            }, status=500)
            
    except Exception as err:
        _LOGGER.error("[web_server] Error saving sensor: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err)
        }, status=500)


async def update_sensor_modes_handler(request):
    """Update sensor mode settings (POST)."""
    try:
        global _db
        
        # Parse request body
        try:
            data = await request.json()
        except Exception as json_err:
            _LOGGER.warning("[web_server] Invalid JSON in request: %s", json_err)
            return web.json_response({
                "success": False,
                "error": "Invalid JSON"
            }, status=400)
        
        entity_id = data.get("entity_id")
        
        if not entity_id:
            return web.json_response({
                "success": False,
                "error": "entity_id is required"
            }, status=400)
        
        enabled_in_away_mode = data.get("enabled_in_away_mode")
        enabled_in_night_mode = data.get("enabled_in_night_mode")
        
        # Convert to boolean if provided (handles both None and explicit False)
        if enabled_in_away_mode is not None:
            enabled_in_away_mode = bool(enabled_in_away_mode)
        if enabled_in_night_mode is not None:
            enabled_in_night_mode = bool(enabled_in_night_mode)
        
        if enabled_in_away_mode is None and enabled_in_night_mode is None:
            return web.json_response({
                "success": False,
                "error": "At least one mode (enabled_in_away_mode or enabled_in_night_mode) must be provided"
            }, status=400)
        
        # Get sensor info for logging
        sensor_info = _db.get_sensor(entity_id)
        sensor_name = sensor_info.get("name", entity_id) if sensor_info else entity_id
        
        # Log mode changes
        if enabled_in_away_mode is not None:
            mode_status = "enabled" if enabled_in_away_mode else "disabled"
            _LOGGER.info("[web_server] 🔧 Sensor mode changed: %s (%s) - Away Mode: %s", 
                        sensor_name, entity_id, mode_status)
        
        if enabled_in_night_mode is not None:
            mode_status = "enabled" if enabled_in_night_mode else "disabled"
            _LOGGER.info("[web_server] 🔧 Sensor mode changed: %s (%s) - Night Mode: %s", 
                        sensor_name, entity_id, mode_status)
        
        _LOGGER.info("[web_server] Updating sensor modes: %s (%s) - away: %s, night: %s", 
                    sensor_name, entity_id, enabled_in_away_mode, enabled_in_night_mode)
        
        success = _db.update_sensor_modes(
            entity_id=entity_id,
            enabled_in_away_mode=enabled_in_away_mode,
            enabled_in_night_mode=enabled_in_night_mode
        )
        
        if success:
            _LOGGER.info("[web_server] ✅ Successfully updated sensor modes for: %s (%s)", 
                        sensor_name, entity_id)
            return web.json_response({
                "success": True,
                "message": "Sensor modes updated successfully"
            })
        else:
            return web.json_response({
                "success": False,
                "error": "Failed to update sensor modes"
            }, status=500)
            
    except Exception as err:
        _LOGGER.error("[web_server] Error updating sensor modes: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err)
        }, status=500)


async def get_background_poll_time_handler(request):
    """Get last background sensor poll time."""
    try:
        global _sensor_monitor
        
        if _sensor_monitor is None:
            return web.json_response({
                "success": True,
                "last_poll_time": None
            })
        
        last_poll_time = _sensor_monitor.get_last_poll_time()
        
        return web.json_response({
            "success": True,
            "last_poll_time": last_poll_time
        })
    except Exception as err:
        _LOGGER.error("[web_server] Error getting background poll time: %s", err, exc_info=True)
        return web.json_response({
            "success": True,
            "last_poll_time": None
        })


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
    """Get virtual switches state and current mode."""
    try:
        global _virtual_switches
        
        # Default states if switches not available
        default_states = {"away": "OFF", "night": "OFF"}
        default_mode = "off"
        
        # Check if switches exist in Home Assistant (created by integration)
        away_exists = await _check_switch_exists("switch.alarmme_away_mode")
        night_exists = await _check_switch_exists("switch.alarmme_night_mode")
        
        if _virtual_switches is None:
            _LOGGER.debug("[web_server] Virtual switches not initialized, returning default states")
            return web.json_response({
                "success": True,
                "mode": default_mode,
                "switches": default_states,
                "connected": False,
                "switches_installed": {
                    "away": away_exists,
                    "night": night_exists
                }
            })
        
        states = _virtual_switches.get_all_states()
        current_mode = _virtual_switches.get_current_mode()
        
        return web.json_response({
            "success": True,
            "mode": current_mode,
            "switches": {
                "away": states.get("away", "OFF"),
                "night": states.get("night", "OFF")
            },
            "connected": _virtual_switches.is_connected if hasattr(_virtual_switches, 'is_connected') else False,
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
            "mode": "off",
            "switches": {"away": "OFF", "night": "OFF"},
            "connected": False,
            "switches_installed": {
                "away": False,
                "night": False
            }
        })


async def update_switches_handler(request):
    """Update virtual switches mode (POST)."""
    try:
        global _virtual_switches
        
        if _virtual_switches is None:
            _LOGGER.warning("[web_server] Virtual switches not initialized")
            return web.json_response({
                "success": False,
                "error": "Virtual switches not initialized"
            }, status=503)
        
        # Parse request body
        try:
            data = await request.json()
        except Exception as json_err:
            _LOGGER.warning("[web_server] Invalid JSON in request: %s", json_err)
            return web.json_response({
                "success": False,
                "error": "Invalid JSON"
            }, status=400)
        
        mode = data.get("mode", "").lower()
        
        if mode not in ("off", "away", "night"):
            _LOGGER.warning("[web_server] Invalid mode: %s", mode)
            return web.json_response({
                "success": False,
                "error": f"Invalid mode: {mode}. Must be 'off', 'away', or 'night'"
            }, status=400)
        
        _LOGGER.info("[web_server] Updating mode to: %s", mode)
        
        # Update switches based on mode
        if mode == "off":
            # Turn off both switches
            away_success = await _virtual_switches.update_switch_state("away", "off")
            night_success = await _virtual_switches.update_switch_state("night", "off")
            success = away_success and night_success
        elif mode == "away":
            # Turn on away, turn off night
            away_success = await _virtual_switches.update_switch_state("away", "on")
            night_success = await _virtual_switches.update_switch_state("night", "off")
            success = away_success and night_success
        elif mode == "night":
            # Turn on night, turn off away
            away_success = await _virtual_switches.update_switch_state("away", "off")
            night_success = await _virtual_switches.update_switch_state("night", "on")
            success = away_success and night_success
        else:
            success = False
        
        if success:
            # Get updated mode
            current_mode = _virtual_switches.get_current_mode()
            _LOGGER.info("[web_server] Successfully updated mode to: %s", current_mode)
            return web.json_response({
                "success": True,
                "mode": current_mode
            })
        else:
            _LOGGER.warning("[web_server] Failed to update mode to: %s", mode)
            return web.json_response({
                "success": False,
                "error": "Failed to update switches"
            }, status=500)
            
    except Exception as err:
        _LOGGER.error("[web_server] Error updating switches: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err)
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
    app.router.add_post("/api/sensors/save", save_sensor_handler)
    app.router.add_post("/api/sensors/update-modes", update_sensor_modes_handler)
    app.router.add_get("/api/background-poll-time", get_background_poll_time_handler)
    app.router.add_get("/api/switches", get_switches_handler)
    app.router.add_post("/api/switches", update_switches_handler)
    
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

