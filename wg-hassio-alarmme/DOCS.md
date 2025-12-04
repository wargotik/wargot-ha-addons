# AlarmMe Add-on Documentation

Complete documentation for installation, configuration, and usage of the AlarmMe add-on for Home Assistant.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Web Interface](#web-interface)
5. [API Reference](#api-reference)
6. [Alarm Modes](#alarm-modes)
7. [Sensor Configuration](#sensor-configuration)
8. [Notifications](#notifications)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Topics](#advanced-topics)

---

## Installation

### Prerequisites

- Home Assistant (Supervised installation)
- Home Assistant Supervisor
- Internet connection (for initial installation)

### Step-by-Step Installation

1. **Add the Repository**
   - Open Home Assistant
   - Go to **Settings** → **Add-ons** → **Repositories**
   - Click **Add** button
   - Enter repository URL: `https://github.com/wargotik/wargot-ha-addons`
   - Click **Add**

2. **Install the Add-on**
   - Go to **Settings** → **Add-ons**
   - Find **AlarmMe** in the add-ons list
   - Click on **AlarmMe**
   - Click **Install** button
   - Wait for installation to complete (usually 1-2 minutes)

3. **Start the Add-on**
   - After installation, go to the **Info** tab
   - Click **Start** button
   - Wait for the add-on to start (check the **Log** tab for status)

4. **Verify Installation**
   - Check the **Log** tab for "AlarmMe add-on started" message
   - Open the **Open Web UI** tab to access the web interface
   - You should see the AlarmMe dashboard

### Post-Installation

After installation, the add-on will:
- Automatically detect your Home Assistant language
- Start monitoring sensors in the background
- Create a persistent notification in Home Assistant
- Initialize the SQLite database for sensor storage

---

## Configuration

### Initial Configuration

The add-on requires **no manual configuration** to start working. It automatically:
- Detects available sensors in Home Assistant
- Saves sensor information to the database
- Monitors sensor states every 5 seconds
- Uses Home Assistant's language setting for the UI

### Configuration Tab

The **Configuration** tab in Home Assistant add-on settings shows:
- **State JSON Info**: Information about the state JSON file location
  - File path: `/data/switches_state.json`
  - View endpoint: `/api/state-json` in web UI

### Custom Integration Setup

For full functionality, install the AlarmMe custom integration:

1. **Install via HACS** (Recommended):
   - Open HACS
   - Go to **Integrations**
   - Click **Custom repositories**
   - Add: `https://github.com/wargotik/wargot-ha-addons`
   - Select category: **Integration**
   - Find **AlarmMe** and click **Install**
   - Restart Home Assistant

2. **Manual Installation**:
   - Copy `custom_components/alarmme` to your Home Assistant `custom_components` directory
   - Restart Home Assistant

The integration creates two virtual switches:
- `switch.alarmme_away_mode` - Away Mode switch
- `switch.alarmme_night_mode` - Night Mode switch

---

## Usage

### Basic Usage

1. **Access the Web Interface**
   - Go to **Settings** → **Add-ons** → **AlarmMe**
   - Click **Open Web UI** tab
   - Or access via Ingress: `http://homeassistant.local:8123/hassio_ingress/wg-hassio-alarmme`

2. **View Sensors**
   - Sensors are automatically discovered and displayed
   - Sensors are grouped by type: Motion, Moving, Occupancy, Presence
   - Each sensor shows:
     - Name and entity ID
     - Current state (on/off)
     - Last triggered time
     - Area/room location
     - Mode buttons (Away/Night)

3. **Configure Sensor Modes**
   - Click **Away** button next to a sensor to enable it for Away Mode
   - Click **Night** button next to a sensor to enable it for Night Mode
   - Active buttons are highlighted in blue (Away) or purple (Night)

4. **Set Alarm Mode**
   - Use the mode buttons at the top:
     - **Off**: Both modes disabled
     - **Away Mode**: Activate when away from home
     - **Night Mode**: Activate when sleeping at home
   - Modes are mutually exclusive (only one can be active at a time)

### Daily Workflow

**Morning (Leaving for Work)**:
1. Open AlarmMe web interface
2. Click **Away Mode** button
3. Verify sensors are enabled for Away Mode
4. Leave home - system is now armed

**Evening (Returning Home)**:
1. Open AlarmMe web interface
2. Click **Off** button to disarm
3. System is now disarmed

**Night (Going to Bed)**:
1. Open AlarmMe web interface
2. Click **Night Mode** button
3. Verify only perimeter sensors are enabled
4. Go to sleep - system monitors entry points

---

## Web Interface

### Main Dashboard

The web interface provides:

- **Header Section**:
  - Add-on icon and version
  - REST API connection status
  - Background update timestamp

- **Current Mode Section**:
  - Current alarm mode (Off/Away/Night)
  - Switch installation status
  - Mode selection buttons
  - Mode descriptions

- **Sensor Grid**:
  - Four columns for sensor types:
    - **Motion** (PIR motion sensors)
    - **Moving** (moving object sensors)
    - **Occupancy** (zone occupancy sensors)
    - **Presence** (static presence sensors)

### Sensor Information

Each sensor displays:
- **Name**: Friendly name from Home Assistant
- **Entity ID**: Full entity identifier
- **State**: Current state (on/off/unknown)
- **Area**: Room/space location (if configured)
- **Last Triggered**: Timestamp of last trigger (DD.MM.YYYY HH:MM:SS)
- **Mode Buttons**: Enable/disable for Away or Night mode
- **Saved Icon**: 💾 indicates sensor is saved in database

### Status Indicators

- **REST API Badge**: Shows connection status to Home Assistant
  - Green: Connected
  - Red: Disconnected
  - Gray: Checking

- **Background Update Badge**: Shows last sensor poll time
  - Format: "X sec/min/h ago at HH:MM:SS"
  - Updates every 5 seconds

---

## API Reference

### Base URL

- **Web UI**: `http://homeassistant.local:8123/hassio_ingress/wg-hassio-alarmme`
- **Direct Access**: `http://homeassistant.local:8099` (if port is exposed)

### Endpoints

#### GET `/api/sensors`

Get all discovered sensors grouped by type.

**Response**:
```json
{
  "success": true,
  "motion_sensors": [...],
  "moving_sensors": [...],
  "occupancy_sensors": [...],
  "presence_sensors": [...]
}
```

**Sensor Object**:
```json
{
  "entity_id": "binary_sensor.motion_sensor",
  "name": "Motion Sensor",
  "device_class": "motion",
  "state": "off",
  "area": "Living Room",
  "enabled_in_away_mode": true,
  "enabled_in_night_mode": false,
  "last_triggered_at": "2025-01-30T12:34:56",
  "saved": true
}
```

#### POST `/api/sensors/save`

Save a sensor to the database (auto-saved on discovery, but can be manually triggered).

**Request**:
```json
{
  "entity_id": "binary_sensor.motion_sensor",
  "name": "Motion Sensor",
  "device_class": "motion"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Sensor saved"
}
```

#### POST `/api/sensors/update-modes`

Update sensor mode configuration (enable/disable for Away or Night mode).

**Request**:
```json
{
  "entity_id": "binary_sensor.motion_sensor",
  "enabled_in_away_mode": true,
  "enabled_in_night_mode": false
}
```

**Response**:
```json
{
  "success": true,
  "message": "Sensor modes updated"
}
```

#### GET `/api/switches`

Get current switch states and mode.

**Response**:
```json
{
  "success": true,
  "mode": "away",
  "connected": true,
  "switches_installed": {
    "away": true,
    "night": true
  }
}
```

#### POST `/api/switches`

Update alarm mode.

**Request**:
```json
{
  "mode": "away"
}
```

**Valid modes**: `"off"`, `"away"`, `"night"`

**Response**:
```json
{
  "success": true,
  "mode": "away"
}
```

#### GET `/api/background-poll-time`

Get last background sensor poll time.

**Response**:
```json
{
  "success": true,
  "last_poll_time": "2025-01-30T12:34:56"
}
```

#### GET `/api/state-json`

Get complete state JSON file content.

**Response**:
```json
{
  "success": true,
  "data": {
    "away": "off",
    "night": "on",
    "language": "en",
    "last_sensor_poll": "2025-01-30T12:34:56"
  },
  "file_path": "/data/switches_state.json",
  "json_string": "{\n  \"away\": \"off\",\n  ...\n}"
}
```

**HTML Format**: Add `?format=html` to get formatted HTML view:
```
GET /api/state-json?format=html
```

#### GET `/health`

Health check endpoint.

**Response**:
```json
{
  "status": "ok"
}
```

---

## Alarm Modes

### Off Mode

**When to use**: System is disarmed, no monitoring active.

**Behavior**:
- All sensors are monitored but no alerts are sent
- Sensor states are still tracked and saved
- Useful for testing or when system is not needed

### Away Mode

**When to use**: You're away from home (work, vacation, errands).

**Configuration**:
- Enable **all sensors** that should trigger alerts
- Typically: all motion, occupancy, and presence sensors
- All areas: living room, bedrooms, kitchen, hallway, etc.

**Example Setup**:
```
✅ Motion sensors: All enabled
✅ Occupancy sensors: All enabled
✅ Presence sensors: All enabled
✅ All rooms: Enabled
```

**Alert Behavior**:
- Any enabled sensor trigger → Immediate alert
- Alert format: "⚠️ ПРОНИКНОВЕНИЕ {area}! Сработал датчик: {sensor_name}"
- Sent to all mobile devices
- Creates persistent notification in Home Assistant

### Night Mode

**When to use**: You're home at night and sleeping.

**Configuration**:
- Enable **perimeter sensors** only
- Entry points: front door, back door, windows, hallway
- Disable: bedroom sensors, bathroom sensors (to avoid false alarms)

**Example Setup**:
```
✅ Front door sensor: Enabled
✅ Back door sensor: Enabled
✅ Hallway motion: Enabled
❌ Bedroom motion: Disabled
❌ Bathroom motion: Disabled
```

**Alert Behavior**:
- Only enabled sensors trigger alerts
- Same alert format as Away Mode
- Designed to avoid false alarms from normal nighttime movement

---

## Sensor Configuration

### Automatic Discovery

Sensors are automatically discovered when:
- They have `device_class` of: `motion`, `moving`, `occupancy`, or `presence`
- They are binary sensors in Home Assistant
- They are polled by the background task every 5 seconds

### Manual Configuration

1. **Enable for Away Mode**:
   - Click **Away** button next to the sensor
   - Button turns blue when active
   - Sensor will trigger alerts in Away Mode

2. **Enable for Night Mode**:
   - Click **Night** button next to the sensor
   - Button turns purple when active
   - Sensor will trigger alerts in Night Mode

3. **Disable for Mode**:
   - Click the active button again to disable
   - Button returns to gray/inactive state

### Sensor States

- **on**: Sensor is triggered (motion/occupancy detected)
- **off**: Sensor is not triggered (no motion/occupancy)
- **unknown**: Sensor state cannot be determined

### Last Triggered Time

- Shows when sensor last changed from `off` to `on`
- Format: `DD.MM.YYYY HH:MM:SS`
- Stored in database with timestamp from Home Assistant
- Updates automatically when sensor triggers

---

## Notifications

### Notification Types

The add-on supports multiple notification methods:

1. **Mobile Notifications**:
   - Automatically detects iPhone and Android devices
   - Sends to all available mobile devices
   - Supports actionable notifications (with buttons)

2. **Persistent Notifications**:
   - Creates permanent notifications in Home Assistant UI
   - Can be dismissed manually
   - Shown in Home Assistant notification panel

### Notification Triggers

Notifications are sent when:

1. **Add-on Startup**:
   - Message: "AlarmMe add-on started"
   - Type: Persistent notification
   - Sent once on startup

2. **Intrusion Detected**:
   - Message: "⚠️ ПРОНИКНОВЕНИЕ {area}! Сработал датчик: {sensor_name}"
   - Type: Mobile + Persistent notification
   - Actionable button: "Отключить тревогу" (Silence Alarm)
   - Sent when:
     - System is in Away Mode or Night Mode
     - A sensor enabled for that mode triggers

### Actionable Notifications

Intrusion alerts include an action button:
- **Title**: "Отключить тревогу" (Silence Alarm)
- **Action**: `SILENCE_ALARM`
- **Usage**: Can be handled via Home Assistant automations

Example automation to handle silence action:
```yaml
automation:
  - alias: "Silence AlarmMe Alarm"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: SILENCE_ALARM
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.alarmme_away_mode
            - switch.alarmme_night_mode
```

---

## Troubleshooting

### Add-on Won't Start

**Symptoms**: Add-on shows "Stopped" status, won't start.

**Solutions**:
1. Check the **Log** tab for error messages
2. Verify Home Assistant is running
3. Check Supervisor API access
4. Restart Home Assistant Supervisor
5. Reinstall the add-on if issues persist

### Sensors Not Appearing

**Symptoms**: No sensors shown in web interface.

**Solutions**:
1. Verify sensors exist in Home Assistant
2. Check sensor `device_class` is one of: `motion`, `moving`, `occupancy`, `presence`
3. Wait 5-10 seconds for background discovery
4. Refresh the web page
5. Check logs for sensor discovery messages

### Notifications Not Sending

**Symptoms**: Alerts not received on mobile devices.

**Solutions**:
1. Verify mobile app is installed and connected
2. Check notification service is available:
   - iPhone: `notify.mobile_app_iphone_*`
   - Android: `notify.mobile_app_android_*`
3. Check add-on logs for notification errors
4. Verify Home Assistant API token is valid
5. Test notification manually via Home Assistant

### Switches Not Found

**Symptoms**: "Switches not installed" message in UI.

**Solutions**:
1. Install AlarmMe custom integration
2. Restart Home Assistant after integration installation
3. Verify switches exist: `switch.alarmme_away_mode`, `switch.alarmme_night_mode`
4. Check integration logs for errors

### Language Not Detected

**Symptoms**: UI shows English instead of your language.

**Solutions**:
1. Verify Home Assistant language is set in settings
2. Check `/data/switches_state.json` contains `"language"` field
3. Restart the add-on to re-detect language
4. Verify translation file exists: `rootfs/translations/{lang}.json`

### Background Polling Not Working

**Symptoms**: "Background update: no data" message.

**Solutions**:
1. Check add-on logs for background task errors
2. Verify sensor monitor started successfully
3. Check database is accessible: `/data/alarmme.db`
4. Restart the add-on

---

## Advanced Topics

### Database Structure

The add-on uses SQLite database at `/data/alarmme.db`.

**Sensors Table**:
```sql
CREATE TABLE sensors (
    entity_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    device_class TEXT NOT NULL,
    enabled_in_away_mode INTEGER DEFAULT 0,
    enabled_in_night_mode INTEGER DEFAULT 0,
    last_triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    area TEXT
);
```

### State File Structure

State is stored in `/data/switches_state.json`:

```json
{
  "away": "off",
  "night": "on",
  "language": "en",
  "last_sensor_poll": "2025-01-30T12:34:56"
}
```

### Background Polling

- **Interval**: 5 seconds
- **Task**: Runs independently of web UI
- **Function**: Polls all sensors, detects triggers, saves to database
- **Logging**: All operations logged to add-on logs

### Language Support

Supported languages:
- English (`en`)
- Polish (`pl`)
- Belarusian (`be`)
- Ukrainian (`uk`)
- Russian (`ru`)

Language is automatically detected from Home Assistant settings and saved to state file.

### Integration with Home Assistant

The add-on integrates with Home Assistant via:

1. **REST API**: For reading sensor states and switch states
2. **Custom Integration**: For creating virtual switches
3. **Notification Services**: For sending alerts
4. **Entity Registry**: For getting sensor areas
5. **Area Registry**: For getting area names

### Automation Examples

**Auto-activate Away Mode when leaving**:
```yaml
automation:
  - alias: "Activate Away Mode on Departure"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: "not_home"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.alarmme_away_mode
```

**Deactivate on arrival**:
```yaml
automation:
  - alias: "Deactivate Alarm on Arrival"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: "home"
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.alarmme_away_mode
            - switch.alarmme_night_mode
```

**Night Mode at bedtime**:
```yaml
automation:
  - alias: "Activate Night Mode at Bedtime"
    trigger:
      - platform: time
        at: "22:00:00"
    condition:
      - condition: state
        entity_id: person.your_name
        state: "home"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.alarmme_night_mode
```

---

## Support

For issues, questions, or contributions:
- **GitHub Repository**: [wargot-ha-addons](https://github.com/wargotik/wargot-ha-addons)
- **Add-on Path**: `wg-hassio-alarmme`

---

## License

This add-on is provided "as is" without warranty.

---

**Last Updated**: 2025-01-30  
**Version**: 0.6.27

