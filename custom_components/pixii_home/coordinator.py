"""Coordinator for Pixii Home integration."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class PixiiHomeDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Pixii Home data."""

    def __init__(self, hass: HomeAssistant, reader, poll_interval: int):
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