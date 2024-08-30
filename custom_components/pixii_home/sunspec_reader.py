import sunspec2.modbus.client as client
import json
import logging
from typing import List, Optional
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

class SunSpecReader:
    def __init__(self, hass: HomeAssistant, host: str, port: int):
        self.hass = hass
        self.host = host
        self.port = port
        self.device = None
        self.models = {}

    async def async_initialize(self):
        try:
            self.device = await self.hass.async_add_executor_job(self._create_device)
            await self.async_scan()
            _LOGGER.info("Successfully connected to SunSpec device at %s:%s", self.host, self.port)
        except Exception as e:
            _LOGGER.error("Failed to connect to SunSpec device at %s:%s: %s", self.host, self.port, str(e))
            raise

    def _create_device(self):
        device = client.SunSpecModbusClientDeviceTCP(slave_id=1, ipaddr=self.host, ipport=self.port)
        return device

    async def async_scan(self):
        """Perform a scan of the device and retrieve data using get_json()."""
        if not self.device:
            _LOGGER.error("No connection to SunSpec device")
            raise HomeAssistantError("No connection to SunSpec device")

        try:
            _LOGGER.debug("Starting device scan")
            await self.hass.async_add_executor_job(self.device.scan)
            _LOGGER.debug("Scan completed. Retrieving JSON data")
            
            json_data = await self.hass.async_add_executor_job(self.device.get_json, True)
            _LOGGER.debug("JSON data retrieved: %s", json_data)
            
            if not json_data:
                _LOGGER.error("Device returned empty JSON data")
                return {}

            data = json.loads(json_data)

            return data
        except Exception as e:
            _LOGGER.exception("Error scanning device and retrieving JSON: %s", str(e))
            return {}

    async def async_read_data(self):
        """Read current data from the device."""
        if not self.device:
            _LOGGER.error("No connection to SunSpec device")
            raise HomeAssistantError("No connection to SunSpec device")

        try:
            # We'll perform a new scan each time to get the most current data
            return await self.async_scan()
        except Exception as e:
            _LOGGER.exception("Error reading data: %s", str(e))
            raise HomeAssistantError(f"Error reading data: {str(e)}")

    async def async_get_debug_data(self):
        data = await self.async_read_data()
        return json.dumps(data, indent=2) if data else None