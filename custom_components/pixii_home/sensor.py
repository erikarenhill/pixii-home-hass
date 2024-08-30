"""Platform for sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    POWER_WATT,
    ENERGY_KILO_WATT_HOUR,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import PixiiHomeDataCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the Pixii Home sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        PixiiHomeBatterySensor(coordinator),
        PixiiHomeChargingSensor(coordinator),
        PixiiHomeDischargingSensor(coordinator),
        PixiiHomeAvailableEnergySensor(coordinator)
    ], True)

class PixiiHomeBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Pixii Home sensors."""

    def __init__(self, coordinator: PixiiHomeDataCoordinator, name: str, unique_id: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{unique_id}"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Pixii Home device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="Pixii Home",
            manufacturer="Pixii",
            model="Battery",
        )

    def _get_battery_data(self):
        """Get the battery data from the coordinator data."""
        if not self.coordinator.data or 'models' not in self.coordinator.data:
            return None
        
        # Find the model with ID 802 (battery model)
        for model in self.coordinator.data['models']:
            if model.get('ID') == 802:
                return model
        return None

class PixiiHomeBatterySensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Battery Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Battery", "battery")
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self):
        """Return the state of the sensor."""
        battery_data = self._get_battery_data()
        if battery_data:
            return battery_data.get("SoC")
        return None

    @property
    def extra_state_attributes(self):
        """Return all attributes of the battery."""
        return self._get_battery_data() or {}

class PixiiHomeChargingSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Charging Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Charging Power", "charging_power")
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        battery_data = self._get_battery_data()
        if battery_data and "W" in battery_data:
            power = battery_data["W"]
            return max(power, 0)  # Only return positive values
        return None

class PixiiHomeDischargingSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Discharging Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Discharging Power", "discharging_power")
        self._attr_native_unit_of_measurement = POWER_WATT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        battery_data = self._get_battery_data()
        if battery_data and "W" in battery_data:
            power = battery_data["W"]
            return abs(min(power, 0))  # Return absolute value of negative power
        return None

class PixiiHomeAvailableEnergySensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Available Energy Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Available Energy", "available_energy")
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def native_value(self):
        """Return the state of the sensor."""
        battery_data = self._get_battery_data()
        if battery_data and "WHRtg" in battery_data and "SoC" in battery_data:
            wh_rating = battery_data["WHRtg"]
            soc = battery_data["SoC"]
            available_wh = (wh_rating * soc) / 100
            return round(available_wh / 1000, 2)  # Convert Wh to kWh and round to 2 decimal places
        return None

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        battery_data = self._get_battery_data()
        if battery_data:
            return {
                "total_capacity_kwh": round(battery_data.get("WHRtg", 0) / 1000, 2),
                "state_of_charge_percent": battery_data.get("SoC", 0)
            }
        return {}