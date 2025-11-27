"""Constants for Communal Apartment integration."""
from __future__ import annotations

DOMAIN = "communal_apartment"
PLATFORMS = ["sensor"]

# Default database path
# Add-on stores database in /data/communal_apartment.db
# If mapped to /config, use /config/communal_apartment.db
# Otherwise, use /data/communal_apartment.db (if accessible)
DEFAULT_DB_PATH = "/data/communal_apartment.db"

# Payment types
PAYMENT_TYPE_ELECTRICITY = "electricity"
PAYMENT_TYPE_GAS = "gas"
PAYMENT_TYPE_WATER = "water"

