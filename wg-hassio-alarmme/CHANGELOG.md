# Changelog

All notable changes to this project will be documented in this file.

## [0.6.27] - 2025-01-30

### Added
- **State JSON endpoint**: Added `/api/state-json` endpoint to view `switches_state.json` file content
- Endpoint supports both JSON and HTML formats (add `?format=html` for HTML view)
- Configuration tab now shows information about state JSON file location
- JSON can be viewed in web UI at `/api/state-json` or `/api/state-json?format=html`

### Changed
- Configuration schema updated to include information about state JSON file

## [0.6.26] - 2025-01-30

### Added
- **Additional language support**: Added Polish, Belarusian, and Ukrainian translations
- Complete translations for all UI texts in Polish (`pl.json`), Belarusian (`be.json`), and Ukrainian (`uk.json`)
- README updated with language badges for all supported languages (English, Polish, Belarusian, Ukrainian, Russian)

### Changed
- Language detection now supports 5 languages: English (en), Polish (pl), Belarusian (be), Ukrainian (uk), Russian (ru)
- UI automatically switches to the appropriate language based on Home Assistant settings

## [0.6.25] - 2025-01-30

### Added
- **Multilingual support**: Added full localization support using JSON translation files
- **English and Russian languages**: Complete translations for all UI texts in English and Russian
- Language automatically detected from Home Assistant settings and applied to UI
- Translation files located in `rootfs/translations/` directory (`en.json`, `ru.json`)
- All UI texts, error messages, and status messages are now translatable
- JavaScript translation function `t()` for client-side translations
- Server-side translation function `_t()` for server-rendered HTML

### Changed
- **UI localization**: All hardcoded texts moved to translation files
- Language is read from `/data/switches_state.json` on each page load
- HTML `lang` attribute dynamically set based on detected language
- README updated with English language support badge

## [0.6.24] - 2025-01-30

### Added
- **Home Assistant language detection**: Added automatic detection and saving of Home Assistant language setting
- Language is fetched from HA API (`/api/config`) on add-on startup
- Language is saved to `/data/switches_state.json` for persistence
- Language code is normalized (e.g., "ru_RU" -> "ru", "en_US" -> "en")
- Falls back to "en" if language cannot be retrieved from HA

## [0.6.23] - 2025-01-30

### Changed
- **Intrusion alert message**: Updated to include sensor area/space in the alert message
- Alert message format: "⚠️ ПРОНИКНОВЕНИЕ {area}! Сработал датчик: {sensor_name}"
- If area is not available, message falls back to: "⚠️ ПРОНИКНОВЕНИЕ! Сработал датчик: {sensor_name}"

## [0.6.22] - 2025-01-30

### Added
- **Area/space support for sensors**: Added ability to get and display the area (space/room) where each sensor is located
- Sensors now automatically fetch area information from Home Assistant Entity Registry and Area Registry
- Area name is saved to database and displayed in UI next to sensor name
- Area information is cached for performance
- Area is automatically updated if it changes in Home Assistant

## [0.6.21] - 2025-01-30

### Fixed
- **Notification service detection**: Fixed `AttributeError: 'list' object has no attribute 'get'` when getting notify services
- `get_available_notify_services()` now correctly handles both dict and list response formats from Home Assistant API
- Mobile notifications should now work correctly when mobile devices are available

## [0.6.20] - 2025-01-30

### Added
- **Add-on icon support**: Added icon display in web UI header
- Icon endpoint `/icon.png` that serves the add-on icon from multiple possible locations
- Icon automatically displayed next to "AlarmMe" title in the web interface
- Icon lookup in `/data/icon.png`, `/icon.png`, and other standard locations

## [0.6.19] - 2025-01-30

### Changed
- **Enhanced logging for notifications**: Added detailed logging to diagnose notification delivery issues
- `get_available_notify_services()` now logs all found notify services and their categorization
- `send_notification()` now logs available mobile services, notification data, and API responses
- `sensor_monitor.py` now logs when notification callback is called and its result
- Improved error messages with full API response text for debugging

## [0.6.18] - 2025-01-30

### Added
- **Actionable notifications**: Added support for action buttons in mobile notifications
- Intrusion alerts now include "Отключить тревогу" (Silence Alarm) button on mobile devices
- `send_notification` now accepts `actions` parameter for actionable notifications
- Actions are automatically added to mobile device notifications (iPhone/Android)
- Persistent notifications in HA UI remain without actions (not supported)

## [0.6.17] - 2025-01-30

### Added
- **Intrusion detection**: When sensor triggers while add-on is in Away or Night mode, and sensor is enabled in that mode, sends alert notification
- Alert message: "⚠️ ПРОНИКНОВЕНИЕ! Сработал датчик: [sensor name]"
- Alert notifications sent to all mobile devices + persistent notification in HA UI
- Automatic mode checking: compares current add-on mode (away/night) with sensor's enabled mode settings

## [0.6.16] - 2025-01-30

### Changed
- Removed "Режим работы" heading from UI for cleaner interface

## [0.6.15] - 2025-01-30

### Changed
- `send_notification` now automatically detects and sends to all available mobile devices (iPhone/Android)
- Added `persistent_notification` parameter to `send_notification` method (default: False)
- Startup notification now includes persistent notification in Home Assistant UI
- Added `get_available_notify_services()` function to detect available mobile devices

### Removed
- Removed `service_name` parameter from `send_notification` - now automatically sends to all devices

## [0.6.14] - 2025-01-30

### Fixed
- Fixed sensor mode toggle buttons (Away/Night) not working - replaced inline onclick with event delegation
- Buttons now use data attributes and event delegation for proper event handling with dynamically generated HTML

## [0.6.13] - 2025-01-30

### Added
- Added detailed logging when sensor modes (Away/Night) are enabled or disabled
- Logs include sensor name, entity_id, and which mode was changed (Away or Night)
- Logs success/failure of mode updates in database

## [0.6.12] - 2025-01-30

### Changed
- Enhanced sensor logging - now logs complete sensor data object from Home Assistant API
- All fields from HA response are now logged: entity_id, state, attributes, last_changed, last_updated, context, etc.
- Uses pprint for readable formatted output of all sensor information

## [0.6.11] - 2025-01-30

### Changed
- Sensor trigger now saves `last_changed` timestamp from Home Assistant instead of current timestamp
- When sensor state is "on" or "true", we now record the exact time when HA detected the state change
- More accurate trigger timestamps - uses HA's `last_changed` field instead of add-on's current time

## [0.6.10] - 2025-01-30

### Changed
- Removed previous_state tracking - trigger detection now based only on current sensor state
- Sensor trigger is recorded when state is "on" or "true" (regardless of previous state)
- Simplified trigger detection logic - no longer tracks state changes, only current active state

## [0.6.9] - 2025-01-30

### Changed
- Added detailed logging for each sensor received from HA API in background task
- Logs include: entity_id, name, device_class, state, and last_updated timestamp
- Helps with debugging and monitoring sensor data from Home Assistant

## [0.6.8] - 2025-01-30

### Changed
- **BREAKING**: UI no longer polls Home Assistant API for sensor discovery
- UI now only reads sensors from database (sensors are saved by background task)
- UI only fetches current states from HA API for display purposes (no saving, no trigger detection)
- Background task is now the only source for:
  - Auto-saving new sensors to database
  - Detecting sensor triggers
  - Recording trigger timestamps
- Improved separation of concerns: background task handles all sensor management, UI only displays data
- UI shows only sensors that are already saved in database by background task

### Removed
- Removed auto-save logic from UI handler (moved to background task)
- Removed trigger detection from UI handler (moved to background task)
- Removed state cache updates from UI handler (only background task updates cache)

## [0.6.7] - 2025-01-30

### Changed
- Added extensive logging to background sensor monitoring task:
  - Logs start of each poll cycle
  - Logs total states received from HA API
  - Logs number of processed sensors (motion/moving/occupancy/presence)
  - Logs number of newly auto-saved sensors
  - Logs number of detected triggers
  - Logs success/failure of trigger recording in database
  - Logs state changes (not just triggers)
  - Logs completion summary with statistics
  - Improved error logging with response body on API errors

## [0.6.6] - 2025-01-30

### Fixed
- Fixed sensor mode toggle buttons (Away/Night) not updating database values
- Improved boolean value handling in API handler to properly convert values to boolean
- Fixed active button styling - buttons now correctly show colored background when enabled:
  - Away mode: blue (#3498db) when active
  - Night mode: purple (#9b59b6) when active
- Added console logging for debugging sensor mode toggles
- Ensured sensor mode values are always properly initialized (default to False if not in database)

## [0.6.5] - 2025-01-30

### Changed
- Sensor last triggered time now shows exact timestamp (DD.MM.YYYY HH:MM:SS) instead of relative time (e.g., "X минут назад")
- Improved clarity by displaying precise time from database

## [0.6.4] - 2025-01-30

### Changed
- Removed UI update badge (browser-based update time)
- Background poll badge now automatically updates every 5 seconds by fetching time from JSON
- Simplified status display to show only REST API connection and background polling status

## [0.6.3] - 2025-01-30

### Changed
- UI update badge now shows "UI обновление: X сек/мин/ч назад в ЧЧ:ММ:СС" for clarity
- Background poll badge format improved to show both relative time and exact time
- Better distinction between UI updates (browser) and background updates (server)

## [0.6.2] - 2025-01-30

### Changed
- Background poll time display now shows both relative time and exact time (e.g., "5 сек назад в 14:30:25")
- Improved time formatting with HH:MM:SS format for better clarity
- Added 'Z' suffix to UTC timestamps for proper ISO format parsing

### Fixed
- Fixed UTC time parsing in JavaScript by adding 'Z' suffix to ISO timestamps
- Added debug logging for sensor monitoring to help diagnose issues

## [0.6.1] - 2025-01-30

### Added
- **Background sensor monitoring**: Sensors are now polled in background every 5 seconds, even when web page is closed
- Background monitoring task runs independently of web UI
- Last background poll time saved to `/data/switches_state.json` (same file as switch states)
- Visual indicator on web page showing time since last background poll (e.g., "Фоновое обновление: 5 сек назад")
- GET API endpoint `/api/background-poll-time` for retrieving last poll time
- Automatic sensor trigger detection in background (logs and saves to database)

### Changed
- Sensor monitoring now works 24/7, not just when web page is open
- Background poll time displayed next to "REST API" badge on main page
- Poll time updates every 5 seconds in UI
- **BREAKING**: Major feature addition - background monitoring significantly changes add-on behavior

## [0.5.6] - 2025-01-30

### Added
- **Background sensor monitoring**: Sensors are now polled in background every 5 seconds, even when web page is closed
- Background monitoring task runs independently of web UI
- Last background poll time saved to `/data/switches_state.json` (same file as switch states)
- Visual indicator on web page showing time since last background poll (e.g., "Фоновое обновление: 5 сек назад")
- GET API endpoint `/api/background-poll-time` for retrieving last poll time
- Automatic sensor trigger detection in background (logs and saves to database)

### Changed
- Sensor monitoring now works 24/7, not just when web page is open
- Background poll time displayed next to "REST API" badge on main page
- Poll time updates every 5 seconds in UI

## [0.5.5] - 2025-01-30

### Added
- **Sensor trigger tracking**: Sensors now track when they trigger (state changes from off to on)
- **Trigger logging**: All sensor triggers are logged with timestamp
- **Last triggered time display**: Each sensor shows time since last trigger (e.g., "5 мин назад", "2 ч назад")
- Database field `last_triggered_at` added to sensors table
- Automatic trigger detection when sensor state changes from off to on
- Visual indicator showing "Последнее срабатывание: X" or "Срабатываний не было" for each sensor

### Changed
- Database schema updated to include `last_triggered_at` timestamp field
- Sensor state changes are now tracked in memory cache for trigger detection
- UI updated to display last trigger time below sensor state

## [0.5.4] - 2025-01-30

### Added
- **Sensor mode buttons**: Added toggle buttons for each sensor to enable/disable in Away Mode and Night Mode
- Mode buttons displayed next to each sensor with visual active state (blue for Away, purple for Night)
- POST API endpoint `/api/sensors/update-modes` for updating sensor mode settings
- JavaScript function `toggleSensorMode()` for handling mode button clicks
- Visual feedback: active buttons are highlighted with mode-specific colors

### Changed
- Sensor items now display mode control buttons below sensor state
- UI updated to show current mode state for each sensor

## [0.5.3] - 2025-01-30

### Added
- **SQLite database for sensors**: Sensors are now automatically saved to `/data/alarmme.db` when detected
- Database module (`database.py`) for managing sensor storage
- Sensor table with fields: `entity_id`, `name`, `device_class`, `enabled_in_away_mode`, `enabled_in_night_mode`
- Automatic sensor saving when detected from Home Assistant API
- Visual indicator (💾 icon) next to sensor name showing it's saved in database
- POST API endpoint `/api/sensors/save` for manual sensor saving (if needed)

### Changed
- Sensors are now automatically persisted to database upon first detection
- UI always shows saved icon for sensors (since they're auto-saved)

## [0.5.2] - 2025-01-30

### Fixed
- Fixed SyntaxError in web_server.py caused by f-string interpretation of CSS and JavaScript code
- Replaced f-string with regular string and `.replace()` method for version substitution
- Fixed Python parser error: "invalid decimal literal" when parsing CSS `repeat(4, 1fr)` syntax

## [0.5.1] - 2025-01-30

### Added
- **Mutually exclusive switch modes**: Switches now work in three exclusive modes:
  - **Off** - both switches disabled
  - **Away Mode** - away mode enabled, night mode disabled
  - **Night Mode** - night mode enabled, away mode disabled
- **Local state storage**: Switch states are now saved to `/data/switches_state.json`
- State persistence across add-on restarts
- **Interactive mode buttons** in web UI for switching between modes
- POST API endpoint `/api/switches` for updating mode programmatically
- Visual mode indicator with color-coded badges (gray for off, blue for away, purple for night)
- Mode buttons with active state highlighting
- Automatic state synchronization between Home Assistant and local storage

### Changed
- **BREAKING**: Switch behavior changed to mutually exclusive - turning on one automatically turns off the other
- UI updated to show single "Режим работы" (Mode) section instead of separate switch displays
- Mode display shows current active mode instead of individual switch states
- Switch state updates now ensure mutual exclusivity
- Monitoring task enforces mutual exclusivity when detecting changes from Home Assistant

### Fixed
- State consistency between Home Assistant and add-on local storage
- Improved state management with automatic conflict resolution

## [0.5.0] - 2025-01-28

### Added
- **Custom Integration**: Added AlarmMe integration (`custom_components/alarmme/`)
- Integration creates two switches: `switch.alarmme_away_mode` and `switch.alarmme_night_mode`
- Switches are grouped in "AlarmMe" device with manufacturer "WarGot"
- Switches have `unique_id` and can be managed from Home Assistant UI
- Switches persist state across restarts using `RestoreEntity`

### Changed
- **BREAKING**: Add-on no longer creates switches via REST API
- Add-on now reads switch states from integration-created switches
- Switches are created by integration, not by add-on
- Entity IDs changed from `input_boolean.*` to `switch.alarmme_*`
- Add-on checks if switches exist and shows "Не установлен" if integration is not installed

### Fixed
- Switches now have proper `unique_id` through integration
- Switches can be fully managed from Home Assistant UI settings
- Device grouping: both switches appear under "AlarmMe" device

## [0.4.2] - 2025-01-28

### Fixed
- Added `unique_id` attribute to input_boolean entities for UI management
- input_boolean entities now have unique identifiers allowing settings management from Home Assistant UI
- Fixed warning: "У этого объекта нет уникального идентификатора"

## [0.4.1] - 2025-01-28

### Changed
- Switched from `switch` to `input_boolean` domain for virtual switches
- Virtual switches now use `input_boolean.alarmme_away_mode` and `input_boolean.alarmme_night_mode`
- Switches now have built-in toggle logic - can be switched directly from Home Assistant UI
- State updates now use `input_boolean/turn_on` and `input_boolean/turn_off` services instead of direct state updates

### Fixed
- Switches can now be toggled from Home Assistant UI (previously only worked via API)
- Better state management using input_boolean services

## [0.4.0] - 2025-01-28

### Changed
- **BREAKING**: Switched from MQTT Discovery to REST API for virtual switches
- Virtual switches now created directly via Home Assistant REST API (`/api/states/`)
- No longer requires MQTT broker - works with just Home Assistant API
- Switches are created automatically on add-on startup
- State monitoring via polling (checks every 2 seconds for changes)
- UI updated to show "REST API: подключен/отключен" instead of MQTT status

### Added
- Automatic state synchronization - detects when switches are changed in Home Assistant UI
- Background monitoring task that polls switch states every 2 seconds
- Callback support for state change notifications

### Removed
- MQTT dependency for virtual switches (paho-mqtt still in requirements but not used)
- MQTT Discovery message publishing
- MQTT connection logic

## [0.3.9] - 2025-01-28

### Changed
- Added additional MQTT host option: "addon_core_mosquitto" (alternative container name)
- Improved MQTT connection fallback logic for different Home Assistant Supervisor setups
- Updated comments to clarify that MQTT is provided by "Mosquitto broker" add-on, not built into HA Core

## [0.3.8] - 2025-01-28

### Added
- Display switch installation status in UI
- Check if virtual switches are installed in Home Assistant via API
- Visual indicator (✓/✗) showing whether each switch is installed or not
- Status updates automatically every 5 seconds along with switch states

## [0.3.7] - 2025-01-28

### Fixed
- Improved MQTT connection logic to try multiple hosts automatically
- Now tries hosts in order: core-mosquitto, localhost, 172.30.32.1
- Better error handling and logging for connection attempts
- Falls back to next host if connection fails

## [0.3.6] - 2025-01-28

### Fixed
- Changed default MQTT host from "core-mosquitto" to "localhost" to match working version 0.3.1

## [0.3.5] - 2025-01-28

### Changed
- Reverted to simpler MQTT connection logic (similar to 0.3.1)
- Removed complex Supervisor API credential fetching that was causing connection issues
- Simplified MQTT initialization - uses direct connection to core-mosquitto
- Removed async start_async method, using simple start() method

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

[0.6.23]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.23
[0.6.22]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.22
[0.6.21]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.21
[0.6.20]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.20
[0.6.19]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.19
[0.6.18]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.18
[0.6.17]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.17
[0.6.16]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.16
[0.6.15]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.15
[0.6.14]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.14
[0.6.13]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.13
[0.6.12]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.12
[0.6.11]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.11
[0.6.10]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.10
[0.6.9]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.9
[0.6.8]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.8
[0.6.7]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.7
[0.6.6]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.6
[0.6.5]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.5
[0.6.4]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.4
[0.6.3]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.3
[0.6.2]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.2
[0.6.1]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.6.1
[0.5.6]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.5.6
[0.5.5]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.5.5
[0.5.4]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.5.4
[0.5.3]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.5.3
[0.5.2]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.5.2
[0.5.1]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.5.1
[0.5.0]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.5.0
[0.4.2]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.4.2
[0.4.1]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.4.1
[0.4.0]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.4.0
[0.3.9]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.9
[0.3.8]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.8
[0.3.7]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.7
[0.3.6]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.6
[0.3.5]: https://github.com/wargotik/wargot-ha-addons/releases/tag/wg-hassio-alarmme-0.3.5
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

