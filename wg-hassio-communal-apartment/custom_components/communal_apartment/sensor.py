"""Sensor platform for Communal Apartment integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PAYMENT_TYPE_ELECTRICITY, PAYMENT_TYPE_GAS, PAYMENT_TYPE_WATER
from .coordinator import CommunalApartmentDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Communal Apartment sensors from a config entry."""
    coordinator: CommunalApartmentDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        CommunalApartmentEnergySensor(coordinator, PAYMENT_TYPE_ELECTRICITY, "Электроэнергия"),
        CommunalApartmentEnergySensor(coordinator, PAYMENT_TYPE_GAS, "Газ"),
        CommunalApartmentEnergySensor(coordinator, PAYMENT_TYPE_WATER, "Вода"),
    ]

    async_add_entities(sensors, update_before_add=True)


class CommunalApartmentEnergySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Communal Apartment energy sensor."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(
        self,
        coordinator: CommunalApartmentDataUpdateCoordinator,
        payment_type: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._payment_type = payment_type
        self._attr_name = f"{name}"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{payment_type}_energy"
        
        # Set device class and unit based on payment type
        if payment_type == PAYMENT_TYPE_ELECTRICITY:
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = "kWh"
        elif payment_type == PAYMENT_TYPE_GAS:
            self._attr_device_class = SensorDeviceClass.GAS
            self._attr_native_unit_of_measurement = "m³"
        elif payment_type == PAYMENT_TYPE_WATER:
            self._attr_device_class = SensorDeviceClass.WATER
            self._attr_native_unit_of_measurement = "m³"
        else:
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = None

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        if self._payment_type in self.coordinator.data:
            total_volume = self.coordinator.data[self._payment_type].get("total_volume", 0.0)
            # Return None if no data yet, otherwise return the value
            if total_volume is None:
                return None
            return float(total_volume)
        
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        attrs = {}
        
        if self.coordinator.data and self._payment_type in self.coordinator.data:
            data = self.coordinator.data[self._payment_type]
            attrs["total_amount"] = data.get("total_amount", 0.0)
            
            last_payment = data.get("last_payment")
            if last_payment:
                attrs["last_payment_date"] = last_payment.get("payment_date")
                attrs["last_payment_amount"] = last_payment.get("amount", 0.0)
                attrs["last_payment_volume"] = last_payment.get("volume")
                attrs["last_payment_period"] = last_payment.get("period")
        
        return attrs

