# AlarmMe Integration for Home Assistant

[![GitHub Release][releases-shield]][releases] ![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

Home Assistant integration for AlarmMe add-on virtual switches.

## Description

This integration creates two virtual switches for the AlarmMe add-on:
- **Away Mode** (Режим отсутствия) - `switch.alarmme_away_mode`
- **Night Mode** (Ночной режим) - `switch.alarmme_night_mode`

Both switches are grouped in the "AlarmMe" device with manufacturer "WarGot".

## Installation

### Option 1: Via HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Go to HACS → **Integrations** → **Custom repositories**
3. Add repository: `https://github.com/wargotik/wargot-ha-addons`
4. Select category: **Integration**
5. Find **AlarmMe** in HACS and click **Install**
6. Restart Home Assistant
7. The integration will automatically load and create the switches

### Option 2: Manual Installation

1. Copy the `alarmme` folder to your `custom_components` directory:
   ```
   <config>/custom_components/alarmme/
   ```

2. Restart Home Assistant

3. The integration will automatically load and create two switches:
   - `switch.alarmme_away_mode` (Режим отсутствия)
   - `switch.alarmme_night_mode` (Ночной режим)

## Features

- Two virtual switches for AlarmMe modes
- Switches grouped in "AlarmMe" device (manufacturer: WarGot)
- State persistence across restarts using `RestoreEntity`
- Full UI management support with `unique_id`
- Automatic add-on availability check on startup

## Usage

The switches can be used in automations, scripts, and Lovelace cards just like any other switch entity.

### Example Automation

```yaml
automation:
  - alias: "Motion detected in away mode"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: 'on'
    condition:
      - condition: state
        entity_id: switch.alarmme_away_mode
        state: 'on'
    action:
      - service: notify.mobile_app_iphone
        data:
          message: "⚠️ Motion detected while away!"
```

## Requirements

- Home Assistant 2023.1.0 or later
- AlarmMe add-on (recommended, for state monitoring)
  - The integration will check if the add-on is available on startup
  - If the add-on is not running, a warning will be logged
  - Switches will still be created, but the add-on won't be able to monitor their state

## Device Information

- **Device Name**: AlarmMe
- **Manufacturer**: WarGot
- **Model**: AlarmMe Add-on
- **Entities**: 
  - `switch.alarmme_away_mode` (Режим отсутствия)
  - `switch.alarmme_night_mode` (Ночной режим)

## Links

- [GitHub Repository][github]
- [Issue Tracker][issues]

[releases-shield]: https://img.shields.io/github/v/release/wargotik/wargot-ha-addons?style=flat-square
[releases]: https://github.com/wargotik/wargot-ha-addons/releases
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg?style=flat-square
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg?style=flat-square
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg?style=flat-square
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg?style=flat-square
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg?style=flat-square
[github]: https://github.com/wargotik/wargot-ha-addons
[issues]: https://github.com/wargotik/wargot-ha-addons/issues

