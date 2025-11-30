# Changelog

All notable changes to this project will be documented in this file.

## [0.3.4] - 2025-01-28

### Added
- MQTT connection status badge on UI
- Visual indicator showing MQTT connection state (connected/disconnected)
- Badge updates automatically every 5 seconds with switch states
- Color-coded badge: green for connected, red for disconnected

## [0.3.3] - 2025-01-28

### Fixed
- Fixed 503 error when MQTT switches not connected - now returns default states (OFF) instead of error
- UI now shows switch states even when MQTT is not connected
- MQTT switches instance is always passed to web_server, allowing UI to work without MQTT connection
- Removed duplicate get_switches_handler function definition

## [0.3.2] - 2025-01-28

### Fixed
- Improved MQTT connection error handling
- Added automatic MQTT credentials fetching from Supervisor API
- Default MQTT host changed to localhost (for add-ons running in Supervisor)
- Better error messages for MQTT connection failures
- Multiple fallback endpoints for getting MQTT credentials

## [0.3.1] - 2025-01-28

### Fixed
- Fixed NameError in mqtt_switches.py when paho-mqtt is not available
- Improved MQTT import error handling

## [0.3.0] - 2025-01-28

### Added
- Virtual switches via MQTT Discovery
- Two switches: "Away Mode" (Режим отсутствия) and "Night Mode" (Ночной режим)
- Switches automatically appear on Home Assistant Overview page
- Switch state display in add-on web UI
- Real-time switch state updates every 5 seconds
- MQTT integration for bidirectional communication (UI ↔ Add-on)
- Switch state persistence in Home Assistant

### Changed
- Switches now managed by add-on via MQTT instead of separate integration
- Added paho-mqtt dependency for MQTT support

## [0.2.1] - 2025-01-28

### Added
- Update badge showing time since last sensor update (e.g., "X секунд назад")
- Badge updates every second to show real-time elapsed time
- Badge displayed next to "AlarmMe add-on is running" text

### Changed
- Sensor refresh interval changed from 5 seconds to 30 seconds
- Improved user experience with visible update status

## [0.2.0] - 2025-01-28

### Added
- Support for tracking 4 types of sensors:
  - **Motion** (device_class: motion) - Classic PIR motion detection
  - **Moving** (device_class: moving) - Moving object detection (cameras/radars)
  - **Occupancy** (device_class: occupancy) - Zone occupancy with delay (motion+presence combo)
  - **Presence** (device_class: presence) - Static human presence (mmWave detects breathing)
- Updated web interface to display 4 columns of sensors
- Responsive grid layout: 2 columns on tablets, 4 columns on desktop

### Changed
- Sensor tracking expanded from 2 types to 4 types
- Improved grid layout for better sensor display

## [0.1.9] - 2025-01-28

### Fixed
- Fixed 404 error when loading sensors - now uses relative path that works with Ingress
- Added 404 handler with logging for better debugging
- Improved logging for all HTTP requests including 404 errors
- Added route registration logging on server startup

## [0.1.8] - 2025-01-28

### Added
- Notification sent automatically when add-on starts
- Notification sent to `mobile_app_iphone` with message "AlarmMe add-on started"

## [0.1.7] - 2025-01-28

### Added
- Function to send notifications via Home Assistant notify service
- Support for sending notifications to mobile apps (e.g., `notify.mobile_app_iphone`)
- Logging for notification sending attempts and results

## [0.1.6] - 2025-01-28

### Changed
- Removed sidebar, sensors now displayed in main content area
- Sensors displayed in two-column grid layout below "AlarmMe add-on is running" message
- Improved responsive design for mobile devices

## [0.1.5] - 2025-01-28

### Added
- Request logging middleware for all HTTP requests
- Enhanced error handling in JavaScript with detailed console logging
- Client IP address logging
- Better error messages in UI showing HTTP status codes and error details
- JSON parsing error handling

### Fixed
- Improved error handling for API responses with non-200 status codes
- Better debugging information in browser console

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

[0.3.4]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.4
[0.3.3]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.3
[0.3.2]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.2
[0.3.1]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.1
[0.3.0]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.0
[0.2.1]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.2.1
[0.2.0]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.2.0
[0.1.9]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.9
[0.1.8]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.8
[0.1.7]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.7
[0.1.6]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.6
[0.1.5]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.5
[0.1.4]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.4
[0.1.3]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.3
[0.1.2]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.2
[0.1.1]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.1.1

