"""Config flow for Pixii Home integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_POLL_INTERVAL
from .sunspec_reader import SunSpecReader

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=502): int,
        vol.Required(CONF_POLL_INTERVAL, default=5): int,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, any]) -> dict[str, any]:
    """Validate the user input allows us to connect."""
    reader = SunSpecReader(hass, data[CONF_HOST], data[CONF_PORT], data[CONF_POLL_INTERVAL])
    
    # if not await hass.async_add_executor_job(reader.test_connection):
    #     raise CannotConnect

    return {"title": f"Pixii Home ({data[CONF_HOST]})"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pixii Home."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""