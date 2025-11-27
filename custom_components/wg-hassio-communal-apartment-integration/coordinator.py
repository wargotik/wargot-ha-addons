"""Data update coordinator for Communal Apartment."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .database import CommunalApartmentDatabase

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=5)


class CommunalApartmentDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the database."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.hass = hass
        self.db_path = entry.data["db_path"]
        self.database = CommunalApartmentDatabase(self.db_path)
    
    @property
    def currency(self) -> str:
        """Get currency from Home Assistant configuration."""
        return getattr(self.hass.config, "currency", "EUR")

    async def _async_update_data(self):
        """Fetch data from database."""
        try:
            _LOGGER.info("Fetching data from database: %s", self.db_path)
            
            # Fetch all payments
            payments = await self.hass.async_add_executor_job(
                self.database.get_all_payments
            )
            
            _LOGGER.info("Retrieved %d payments from database", len(payments))
            
            # Calculate totals by payment type
            data = {
                "payments": payments,
                "electricity": {
                    "total_amount": 0.0,
                    "total_volume": 0.0,
                    "last_payment": None,
                },
                "gas": {
                    "total_amount": 0.0,
                    "total_volume": 0.0,
                    "last_payment": None,
                },
                "water": {
                    "total_amount": 0.0,
                    "total_volume": 0.0,
                    "last_payment": None,
                },
            }
            
            # Process payments - use system_name directly from payment
            for payment in payments:
                system_name = payment.get("system_name", "")
                
                if system_name in data:
                    amount = payment.get("amount", 0.0) or 0.0
                    volume = payment.get("volume") or 0.0
                    
                    _LOGGER.debug("Processing payment: system_name=%s, amount=%s, volume=%s", 
                                 system_name, amount, volume)
                    
                    data[system_name]["total_amount"] += amount
                    if volume:
                        data[system_name]["total_volume"] += volume
                    
                    # Track last payment
                    payment_date = payment.get("payment_date")
                    if payment_date:
                        if data[system_name]["last_payment"] is None:
                            data[system_name]["last_payment"] = payment
                        else:
                            last_date = data[system_name]["last_payment"].get("payment_date", "")
                            if payment_date > last_date:
                                data[system_name]["last_payment"] = payment
            
            _LOGGER.info("Calculated totals: electricity=%s, gas=%s, water=%s",
                        data["electricity"]["total_volume"],
                        data["gas"]["total_volume"],
                        data["water"]["total_volume"])
            
            return data
        except Exception as err:
            _LOGGER.error("Error communicating with database: %s", err, exc_info=True)
            raise UpdateFailed(f"Error communicating with database: {err}")
