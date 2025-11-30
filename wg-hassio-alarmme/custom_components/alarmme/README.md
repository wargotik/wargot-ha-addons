# AlarmMe Integration

Home Assistant integration for AlarmMe add-on virtual switches.

## Installation

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
- Switches grouped in "AlarmMe" device
- State persistence across restarts
- Full UI management support with unique_id
- Manufacturer: WarGot

## Usage

The switches can be used in automations, scripts, and Lovelace cards just like any other switch entity.

## Requirements

- Home Assistant 2023.1 or later
- AlarmMe add-on (recommended, for state monitoring)
  - The integration will check if the add-on is available on startup
  - If the add-on is not running, a warning will be logged
  - Switches will still be created, but the add-on won't be able to monitor their state

