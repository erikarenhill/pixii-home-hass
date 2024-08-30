"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta
import logging
import json

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_POLL_INTERVAL, DOMAIN
from .sunspec_reader import SunSpecReader

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the Pixii Home sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PixiiHomeBatterySensor(coordinator)], True)

class PixiiHomeDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Pixii Home data."""

    def __init__(self, hass, reader, poll_interval):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self.reader = reader
        self.data = None

    async def _async_update_data(self):
        """Fetch data from Pixii Home reader."""
        self.data = await self.reader.async_read_data()
        _LOGGER.debug("All Data:\n%s", json.dumps(self.data, indent=2))
        return self.data

class PixiiHomeBatterySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Pixii Home Battery Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Pixii Home Battery"
        self._attr_unique_id = f"{DOMAIN}_battery"
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Pixii Home device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="Pixii Home",
            manufacturer="Pixii",
            model="Battery",
        )

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

    def _get_battery_data(self):
        """Get the battery data from the coordinator data."""
        if not self.coordinator.data or 'models' not in self.coordinator.data:
            return None
        
        # Find the model with ID 802 (battery model)
        for model in self.coordinator.data['models']:
            if model.get('ID') == 802:
                return model
        return None