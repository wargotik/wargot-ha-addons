# Utilities Tracker Sensors Integration for Home Assistant

[![GitHub Release][releases-shield]][releases] ![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

Home Assistant integration for the Utilities Tracker add-on, providing sensors for the Energy Dashboard.

## Description

This integration creates energy sensors for Home Assistant Energy Dashboard based on data from the Utilities Tracker add-on. The integration reads data from the add-on's SQLite database and creates three sensors:

- **Electricity** (device_class: energy, unit: kWh)
- **Gas** (device_class: gas, unit: m³)
- **Water** (device_class: water, unit: m³)

## Installation

### Option 1: Manual Installation

1. Copy the `custom_components/wg-hassio-communal-apartment-integration/` folder to your Home Assistant `/config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for **Utilities Tracker Sensors Integration** and click **Configure**
5. Enter the database path (default: `/config/communal_apartment.db`)

### Option 2: Via HACS (Home Assistant Community Store)

1. Install HACS if you haven't already
2. Go to HACS → **Integrations** → **Custom repositories**
3. Add repository: `https://github.com/wargotik/wargot-ha-addons`
4. Find **Utilities Tracker Sensors Integration** in HACS and install it
5. Restart Home Assistant
6. Add the integration via **Settings** → **Devices & Services**

## Configuration

When adding the integration, specify the path to the database:

- **Default**: `/config/communal_apartment.db` (if the add-on's database is mounted to `/config`)
- **Alternative**: `/data/communal_apartment.db` (if the database is located in `/data`)

## Usage

After installing the integration, three sensors are automatically created:

- `sensor.elektroenergiya` - Electricity (kWh)
- `sensor.gaz` - Gas (m³)
- `sensor.voda` - Water (m³)

These sensors are automatically available for use in Home Assistant's **Energy Dashboard**.

### Sensor Attributes

Each sensor has the following attributes:

- `total_amount` - Total amount of payments
- `last_payment_date` - Date of the last payment
- `last_payment_amount` - Amount of the last payment
- `last_payment_volume` - Volume of the last payment
- `last_payment_period` - Period of the last payment

## Requirements

- Home Assistant version 2022.5 or higher
- Installed and running Utilities Tracker add-on
- Access to the add-on's database

## Features

- **Energy Dashboard Integration**: Automatically creates sensors compatible with Home Assistant Energy Dashboard
- **Real-time Updates**: Data is updated every 5 minutes
- **Multiple Payment Types**: Supports electricity, gas, and water payments
- **Detailed Attributes**: Provides comprehensive information about payments

## Version

Current version: 0.1.3

## Support

If you encounter any issues, please check:

1. Correctness of the database path
2. Database file accessibility for reading
3. Home Assistant logs for errors

## Links

- [Add-on Repository](https://github.com/wargotik/wargot-ha-addons)
- [Issues](https://github.com/wargotik/wargot-ha-addons/issues)

---

[releases-shield]: https://img.shields.io/github/v/release/wargotik/wargot-ha-addons.svg?style=flat-square
[releases]: https://github.com/wargotik/wargot-ha-addons/releases
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg?style=flat-square
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg?style=flat-square
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg?style=flat-square
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg?style=flat-square
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg?style=flat-square
