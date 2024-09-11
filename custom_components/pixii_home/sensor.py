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
    FREQUENCY_HERTZ,
    TEMP_CELSIUS,
    __version__ as HA_VERSION,
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
        PixiiHomeAvailableEnergySensor(coordinator),
        PixiiHomeUsableEnergySensor(coordinator),
        PixiiHomeInfoSensor(coordinator),
        PixiiHomeInverterSensor(coordinator),
        PixiiHomeFrequencySensor(coordinator),
        PixiiHomeCabinetTempSensor(coordinator),
        PixiiHomeTransformerTempSensor(coordinator),
        PixiiHomeStateSensor(coordinator),
        PixiiHomeVendorStateSensor(coordinator),
        PixiiHomeFirmwareVersionSensor(coordinator),
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
        info_data = self._get_info_data()
        if info_data:
            return DeviceInfo(
                identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
                name="Pixii Home",
                manufacturer=info_data.get("Mn", "Pixii"),
                model=info_data.get("Md", "Battery"),
                sw_version=info_data.get("Vr", "Unknown"),
                hw_version=info_data.get("SN", "Unknown"),
            )
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="Pixii Home",
            manufacturer="Pixii",
            model="Battery",
        )

    def _get_data(self, id):
        """Get the data from the coordinator data."""
        if not self.coordinator.data or 'models' not in self.coordinator.data:
            return None
        
        # Find the model with ID 1
        for model in self.coordinator.data['models']:
            if model.get('ID') == id:
                return model
            
        return None
    

    def _get_info_data(self):
        return self._get_data(1)
    
    def _get_inverter_data(self):
        return self._get_data(103)

    def _get_battery_data(self):
        return self._get_data(802)

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

class PixiiHomeUsableEnergySensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Usable Energy Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Usable Energy Left", "usable_energy")
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    @property
    def native_value(self):
        """Return the state of the sensor."""
        battery_data = self._get_battery_data()
        if battery_data and all(key in battery_data for key in ["WHRtg", "SoC", "SoCRsvMin"]):
            wh_rating = battery_data["WHRtg"]
            current_soc = battery_data["SoC"]
            min_soc = battery_data["SoCRsvMin"]
            
            usable_soc = max(current_soc - min_soc, 0)  # Ensure non-negative value
            usable_wh = (wh_rating * usable_soc) / 100
            return round(usable_wh / 1000, 2)  # Convert Wh to kWh and round to 2 decimal places
        return None

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        battery_data = self._get_battery_data()
        if battery_data:
            return {
                "current_soc_percent": battery_data.get("SoC", 0),
                "min_soc_percent": battery_data.get("SoCRsvMin", 0),
                "max_soc_percent": battery_data.get("SocRsvMax", 0),
                "total_capacity_kwh": round(battery_data.get("WHRtg", 0) / 1000, 2),
            }
        return {}

class PixiiHomeInfoSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Info Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Info", "info")
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        info_data = self._get_info_data()
        if info_data:
            return f"{info_data.get('Mn', 'Unknown')} {info_data.get('Md', 'Unknown')}"
        return None

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        info_data = self._get_info_data()
        if info_data:
            return {
                "manufacturer": info_data.get("Mn", "Unknown"),
                "model": info_data.get("Md", "Unknown"),
                "version": info_data.get("Vr", "Unknown"),
                "serial_number": info_data.get("SN", "Unknown")
            }
        return {}

class PixiiHomeInverterSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Inverter Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Inverter", "inverter")
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        inverter_data = self._get_inverter_data()
        if inverter_data:
            return "Online"
        return "Offline"

    @property
    def extra_state_attributes(self):
        """Return all attributes of the inverter."""
        return self._get_inverter_data() or {}

class PixiiHomeFrequencySensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Frequency Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Frequency", "frequency")
        self._attr_device_class = SensorDeviceClass.FREQUENCY
        self._attr_native_unit_of_measurement = FREQUENCY_HERTZ

    @property
    def native_value(self):
        """Return the state of the sensor."""
        inverter_data = self._get_inverter_data()
        if inverter_data and "Hz" in inverter_data:
            return inverter_data["Hz"]
        return None

class PixiiHomeCabinetTempSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Cabinet Temperature Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Cabinet Temperature", "cabinet_temp")
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = TEMP_CELSIUS

    @property
    def native_value(self):
        """Return the state of the sensor."""
        inverter_data = self._get_inverter_data()
        if inverter_data and "TmpCab" in inverter_data:
            return inverter_data["TmpCab"]
        return None

class PixiiHomeTransformerTempSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Transformer Temperature Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Transformer Temperature", "transformer_temp")
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = TEMP_CELSIUS

    @property
    def native_value(self):
        """Return the state of the sensor."""
        inverter_data = self._get_inverter_data()
        if inverter_data and "TmpTrns" in inverter_data:
            return inverter_data["TmpTrns"]
        return None

class PixiiHomeStateSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home State Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home State", "state")
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        inverter_data = self._get_inverter_data()
        if inverter_data and "St" in inverter_data:
            return inverter_data["St"]
        return None

class PixiiHomeVendorStateSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Vendor State Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Vendor State", "vendor_state")
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        inverter_data = self._get_inverter_data()
        if inverter_data and "StVnd" in inverter_data:
            return inverter_data["StVnd"]
        return None

class PixiiHomeFirmwareVersionSensor(PixiiHomeBaseSensor):
    """Representation of a Pixii Home Firmware Version Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "Pixii Home Firmware Version", "firmware_version")
        self._attr_device_class = None
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        """Return the firmware version."""
        info_data = self._get_info_data()
        if info_data and "Vr" in info_data:
            return info_data["Vr"]
        return None

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "home_assistant_version": HA_VERSION,
        }