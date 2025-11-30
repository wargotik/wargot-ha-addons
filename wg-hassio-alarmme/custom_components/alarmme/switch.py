"""AlarmMe switch platform."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DOMAIN = "alarmme"


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up AlarmMe switches."""
    async_add_entities([
        AlarmMeSwitch(hass, "away", "Away Mode", "Режим отсутствия", "mdi:shield-home"),
        AlarmMeSwitch(hass, "night", "Night Mode", "Ночной режим", "mdi:weather-night"),
    ])


class AlarmMeSwitch(SwitchEntity, RestoreEntity):
    """Representation of an AlarmMe switch."""

    _attr_should_poll = False
    _attr_assumed_state = False

    def __init__(
        self,
        hass: HomeAssistant,
        switch_type: str,
        name: str,
        friendly_name: str,
        icon: str,
    ) -> None:
        """Initialize the AlarmMe switch."""
        self._hass = hass
        self._switch_type = switch_type
        self._attr_name = friendly_name
        self._attr_unique_id = f"alarmme_{switch_type}_mode"
        self._attr_icon = icon
        self._attr_is_on = False

        # Device info - creates "AlarmMe" device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "alarmme_device")},
            name="AlarmMe",
            manufacturer="WarGot",
            model="AlarmMe Add-on",
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Restore state on startup."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state == "on":
                self._attr_is_on = True
            elif last_state.state == "off":
                self._attr_is_on = False

