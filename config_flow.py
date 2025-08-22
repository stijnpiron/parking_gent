"""Config flow for Parking Gent integration."""
from __future__ import annotations

import logging
from typing import Any

import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .constants import API_PARKING, API_PR, API_TIMEOUT, FIELDS_GARAGE, FIELDS_PR

_LOGGER = logging.getLogger(__name__)

CONF_SELECTED_PARKINGS = "selected_parkings"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default="Parking Gent"): str,
    }
)


async def get_available_parkings(hass: HomeAssistant) -> dict[str, list[str]]:
    """Get all available parking locations from APIs."""
    apis_to_check = [
        ("Parking Garages", API_PARKING, FIELDS_GARAGE),
        ("P+R Parking", API_PR, FIELDS_PR),
    ]
    
    available_parkings = {}
    
    for api_name, api_url, fields in apis_to_check:
        try:
            response = await hass.async_add_executor_job(
                lambda: requests.get(api_url, timeout=API_TIMEOUT)
            )
            response.raise_for_status()
            
            api_data = response.json()
            if "results" not in api_data:
                continue
            
            parkings = []
            for record in api_data.get("results", []):
                name = record.get(fields["name"])
                if name:
                    parkings.append(name)
            
            if parkings:
                available_parkings[api_name] = sorted(parkings)
                _LOGGER.debug("Found %d parkings in %s API", len(parkings), api_name)
            
        except Exception as err:
            _LOGGER.debug("Failed to fetch parkings from %s API: %s", api_name, err)
            continue
    
    return available_parkings


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Test API connectivity
    available_parkings = await get_available_parkings(hass)
    
    if not available_parkings:
        raise CannotConnect("All parking APIs are unavailable")
    
    total_parkings = sum(len(parkings) for parkings in available_parkings.values())
    _LOGGER.debug("Found %d total parking locations across %d APIs", 
                  total_parkings, len(available_parkings))
    
    return {
        "title": data[CONF_NAME], 
        "available_parkings": available_parkings,
        "total_parkings": total_parkings
    }


class ConfigFlow(config_entries.ConfigFlow, domain="parking_gent"):
    """Handle a config flow for Parking Gent."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self._available_parkings = {}
        self._name = "Parking Gent"

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["base"] = "invalid_host"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id("parking_gent")
                self._abort_if_unique_id_configured()
                
                # Store available parkings and name for next step
                self._available_parkings = info["available_parkings"]
                self._name = info["title"]
                
                # If no parkings found, can't continue
                if not self._available_parkings:
                    errors["base"] = "no_parkings"
                else:
                    return await self.async_step_select_parkings()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_select_parkings(self, user_input=None):
        """Let user select which parkings to include."""
        errors = {}
        
        # Create options for multi-select
        parking_options = []
        for api_name, parkings in self._available_parkings.items():
            for parking in parkings:
                parking_options.append({
                    "value": parking,
                    "label": f"{parking} ({api_name})"
                })
        
        # Sort by label for better UX
        parking_options.sort(key=lambda x: x["label"])
        
        # Default to all parkings selected
        default_selected = [opt["value"] for opt in parking_options]
        
        data_schema = vol.Schema({
            vol.Required(
                CONF_SELECTED_PARKINGS,
                default=default_selected
            ): SelectSelector(
                SelectSelectorConfig(
                    options=parking_options,
                    multiple=True,
                    mode=SelectSelectorMode.LIST
                )
            )
        })

        if user_input is not None:
            selected_parkings = user_input.get(CONF_SELECTED_PARKINGS, [])
            
            if not selected_parkings:
                errors["base"] = "no_parkings_selected"
            else:
                # Create the config entry
                return self.async_create_entry(
                    title=self._name,
                    data={
                        CONF_NAME: self._name,
                        CONF_SELECTED_PARKINGS: selected_parkings,
                    }
                )

        return self.async_show_form(
            step_id="select_parkings",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "total_available": str(len(parking_options))
            }
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Parking Gent."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self._available_parkings = {}

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        
        # Get available parkings
        try:
            self._available_parkings = await get_available_parkings(self.hass)
        except Exception:
            errors["base"] = "cannot_connect"
            return self.async_show_form(
                step_id="init",
                errors=errors
            )
        
        # Create options for multi-select
        parking_options = []
        for api_name, parkings in self._available_parkings.items():
            for parking in parkings:
                parking_options.append({
                    "value": parking,
                    "label": f"{parking} ({api_name})"
                })
        
        # Sort by label for better UX
        parking_options.sort(key=lambda x: x["label"])
        
        # Get current selection
        current_selected = self.config_entry.data.get(CONF_SELECTED_PARKINGS, [])
        
        data_schema = vol.Schema({
            vol.Required(
                CONF_SELECTED_PARKINGS,
                default=current_selected
            ): SelectSelector(
                SelectSelectorConfig(
                    options=parking_options,
                    multiple=True,
                    mode=SelectSelectorMode.LIST
                )
            )
        })

        if user_input is not None:
            selected_parkings = user_input.get(CONF_SELECTED_PARKINGS, [])
            
            if not selected_parkings:
                errors["base"] = "no_parkings_selected"
            else:
                # Update the config entry
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        **self.config_entry.data,
                        CONF_SELECTED_PARKINGS: selected_parkings,
                    }
                )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "total_available": str(len(parking_options)),
                "currently_selected": str(len(current_selected))
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
