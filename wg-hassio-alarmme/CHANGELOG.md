# Changelog

All notable changes to this project will be documented in this file.

## [0.1.4] - 2025-01-28

### Added
- Detailed logging for sensor list requests
- Logging of request start, HA API calls, and response processing
- Debug logging for each found sensor with entity_id, name, and state
- Logging of total states received and processed sensors count

## [0.1.3] - 2025-01-28

### Added
- Sidebar with motion and occupancy sensors
- Two columns: "Датчики движения" (Motion Sensors) and "Датчики присутствия" (Occupancy Sensors)
- Automatic detection of sensors with device_class: motion and device_class: occupancy
- Real-time sensor state display with color indicators
- Auto-refresh sensors every 5 seconds
- Home Assistant API integration for fetching sensor data

## [0.1.2] - 2025-01-28

### Added
- AlarmMe integration with virtual switch entity
- Switch automatically appears on Home Assistant Overview page
- Switch state persistence across restarts

## [0.1.1] - 2025-01-28

### Added
- Initial release of AlarmMe add-on
- Basic web server with health check endpoint
- Docker container setup
- Home Assistant add-on configuration

[0.1.4]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.4
[0.1.3]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.3
[0.1.2]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.2
[0.1.1]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.1

