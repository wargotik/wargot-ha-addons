# Utilities Tracker Add-on for Home Assistant

[![GitHub Release][releases-shield]][releases] ![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

Add-on for tracking utility payments (electricity, gas, water) with a web interface and integration with Home Assistant Energy Dashboard.

## Description

This add-on provides a utility payment tracking system (electricity, gas, water) with a web interface for managing payments and integration with Home Assistant Energy Dashboard. Data is stored in a local SQLite database.

## Installation

1. Add the repository to Home Assistant:
   - Go to **Settings** → **Add-ons** → **Repositories**
   - Add: `https://github.com/wargotik/wargot-ha-addons`
   - Click **Add**

2. Install the add-on:
   - Go to **Settings** → **Add-ons**
   - Find **Utilities Tracker** in the list
   - Click **Install**

## Configuration

After installation, the add-on is ready to use. No additional configuration is required.

For integration with Home Assistant Energy Dashboard:
1. Install the "Utilities Tracker" integration from the repository
2. Specify the database path (default: `/data/communal_apartment.db`)
3. Sensors will automatically appear in the system

## Usage

1. Start the add-on via the **Info** tab
2. Open the web interface via the **Open Web UI** tab or through Ingress
3. Add payments through the web interface
4. View statistics in Home Assistant Energy Dashboard

## Features

- **Web Interface** for managing payments
- **Multilingual Support**: English, Russian, Ukrainian, Polish, Belarusian
- **Automatic Currency Detection** from Home Assistant settings
- **Volume Calculation** based on meter readings
- **Unit Price Calculation** (unit_price)
- **Energy Dashboard Integration** with Home Assistant
- **Payment Type Support**: Electricity, Gas, Water

## Data Storage

Payment data is stored in a SQLite database:
```
/data/communal_apartment.db
```

## Logs

All add-on logs are available on the **Log** tab. There you can see:
- Payment saving process
- Errors if they occur
- Web server information

## Support

If you encounter any issues, please check:
1. The **Log** tab for errors
2. Web interface availability
3. Correctness of the database path in the integration

## Version

Current version: 0.4.8

## Links

- [Repository][repository]
- [Issues][issues]

[releases-shield]: https://img.shields.io/github/release/wargotik/wargot-ha-addons.svg?style=flat-square
[releases]: https://github.com/wargotik/wargot-ha-addons/releases
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[repository]: https://github.com/wargotik/wargot-ha-addons
[issues]: https://github.com/wargotik/wargot-ha-addons/issues
