# AlarmMe Add-on for Home Assistant

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

![Russian Language][ru-shield]

AlarmMe add-on for Home Assistant.

## Description

AlarmMe is a comprehensive alarm management add-on for Home Assistant that provides intelligent intrusion detection, sensor monitoring, and notification capabilities. The add-on automatically monitors motion, occupancy, and presence sensors, detects intrusions when the system is armed, and sends alerts to all your mobile devices.

## Installation

1. Add the repository to Home Assistant:
   - Go to **Settings** → **Add-ons** → **Repositories**
   - Add: `https://github.com/wargotik/wargot-ha-addons`
   - Click **Add**

2. Install the add-on:
   - Go to **Settings** → **Add-ons**
   - Find **AlarmMe** in the list
   - Click **Install**

## Configuration

After installation, the add-on is ready to use. No additional configuration is required.

## Usage

1. Start the add-on via the **Info** tab
2. Open the web interface via the **Open Web UI** tab or through Ingress

## Features

### Core Functionality

- **🖥️ Modern Web Interface**: Clean, responsive web UI for managing your alarm system
- **🔄 Background Sensor Monitoring**: Automatically polls sensors every 5 seconds, even when the web page is closed
- **📊 SQLite Database**: Persistent storage for sensor configurations, trigger history, and settings
- **🏠 Home Assistant Integration**: Seamless integration with Home Assistant via REST API and custom integration

### Alarm Modes

- **🚪 Away Mode**: Activate when you're away from home
- **🌙 Night Mode**: Activate for nighttime security
- **⚙️ Mutually Exclusive Modes**: Only one mode can be active at a time (Off, Away, or Night)
- **💾 Local State Storage**: Switch states persist across restarts in `/data/switches_state.json`

### Sensor Management

- **🔍 Automatic Sensor Discovery**: Automatically detects and saves motion, moving, occupancy, and presence sensors
- **📍 Area/Space Support**: Automatically fetches and displays the room/area where each sensor is located
- **⚡ Sensor Trigger Detection**: Detects when sensors change from "off" to "on" state
- **📝 Trigger History**: Tracks and displays the exact timestamp of the last sensor trigger
- **🎯 Per-Sensor Mode Configuration**: Enable/disable individual sensors for Away Mode or Night Mode
- **💾 Auto-Save**: New sensors are automatically saved to the database upon detection

### Intrusion Detection

- **🚨 Intelligent Intrusion Detection**: Automatically detects intrusions when:
  - Add-on is in Away Mode or Night Mode
  - A sensor triggers (state = "on")
  - The sensor is enabled for the current mode
- **📱 Multi-Channel Notifications**: Sends alerts via:
  - All available mobile devices (iPhone/Android)
  - Persistent notifications in Home Assistant UI
- **🔘 Actionable Notifications**: Mobile notifications include "Отключить тревогу" (Silence Alarm) button
- **📍 Contextual Alerts**: Alert messages include sensor area/space for better context:
  - Format: "⚠️ ПРОНИКНОВЕНИЕ {area}! Сработал датчик: {sensor_name}"

### Notifications

- **📱 Automatic Device Detection**: Automatically discovers and sends to all available mobile devices
- **🔔 Persistent Notifications**: Optional persistent notifications in Home Assistant UI
- **⚙️ Actionable Notifications**: Interactive buttons in mobile notifications (iOS/Android)
- **📊 Notification Logging**: Detailed logging for debugging notification delivery

### User Interface

- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🎨 Modern UI**: Clean, intuitive interface with color-coded status indicators
- **🔄 Real-Time Updates**: Live updates of sensor states, switch modes, and background poll times
- **📊 Status Badges**: Visual indicators for:
  - REST API connection status
  - Background sensor polling time
  - Current alarm mode
- **🖼️ Add-on Icon**: Custom icon support displayed in the web interface header

### Technical Features

- **🔌 REST API**: Full REST API for programmatic control and integration
- **📝 Comprehensive Logging**: Detailed logging for all operations and errors
- **⚡ Performance Optimized**: Area information caching, efficient database queries
- **🔄 State Synchronization**: Automatic synchronization between Home Assistant and local storage
- **🌐 Ingress Support**: Accessible via Home Assistant Ingress (no port forwarding needed)

## Support

For issues, questions, or contributions, please visit the [GitHub repository][repository].

## License

This add-on is provided as-is.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[ru-shield]: https://img.shields.io/badge/🇷🇺%20Russian-supported-blue.svg
[repository]: https://github.com/wargotik/wargot-ha-addons/tree/master/wg-hassio-alarmme

