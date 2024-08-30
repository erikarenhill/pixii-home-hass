from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging
import json

from .const import DOMAIN, CONF_POLL_INTERVAL
from .sunspec_reader import SunSpecReader
from .sensor import PixiiHomeDataCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pixii Home from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    poll_interval = entry.data[CONF_POLL_INTERVAL]

    reader = SunSpecReader(hass, host, port)

    try:
        await reader.async_initialize()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to connect to Pixii Home: {err}") from err

    coordinator = PixiiHomeDataCoordinator(hass, reader, poll_interval)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok