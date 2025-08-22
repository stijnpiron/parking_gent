"""The Parking Gent integration."""

import asyncio
import logging
import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .constants import API_PARKING, API_PR, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Parking Gent from a config entry."""
    
    # Test API connectivity before setting up platforms
    session = async_get_clientsession(hass)
    
    try:
        await _test_api_connectivity(hass, session)
    except Exception as err:
        _LOGGER.error("Failed to connect to Parking Gent API during setup: %s", err)
        raise ConfigEntryNotReady(f"Unable to connect to Parking Gent API: {err}") from err
    
    # Store the session for use by platforms
    hass.data.setdefault("parking_gent", {})
    hass.data["parking_gent"][entry.entry_id] = {
        "session": session,
    }
    
    # Forward the setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Set up listener for config entry updates
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry updates."""
    _LOGGER.debug("Config entry updated, reloading integration")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data["parking_gent"].pop(entry.entry_id)
    
    return unload_ok


async def _test_api_connectivity(hass: HomeAssistant, session) -> None:
    """Test connectivity to all parking APIs."""
    apis_to_test = [
        ("Parking Garages", API_PARKING),
        ("P+R Parking", API_PR),
    ]
    
    errors = []
    
    for api_name, api_url in apis_to_test:
        try:
            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug("Testing connectivity to %s API: %s", api_name, api_url)
            
            # Use executor job for requests since we don't have aiohttp session yet
            response = await hass.async_add_executor_job(
                lambda: requests.get(api_url, timeout=API_TIMEOUT)
            )
            response.raise_for_status()
            
            # Check if response has expected structure
            data = response.json()
            if "results" not in data:
                raise ValueError(f"API response missing 'results' field")
            
            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug("Successfully connected to %s API", api_name)
            
        except requests.exceptions.RequestException as err:
            error_msg = f"Failed to connect to {api_name} API: {err}"
            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug(error_msg)
            errors.append(error_msg)
        except ValueError as err:
            error_msg = f"Invalid response from {api_name} API: {err}"
            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug(error_msg)
            errors.append(error_msg)
        except Exception as err:
            error_msg = f"Unexpected error with {api_name} API: {err}"
            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug(error_msg)
            errors.append(error_msg)
    
    # If all APIs failed, raise an exception
    if len(errors) == len(apis_to_test):
        raise ConnectionError(f"All parking APIs are unavailable: {'; '.join(errors)}")
    
    # If some APIs failed, log warnings but continue
    if errors:
        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug(
                "Some parking APIs are unavailable, but continuing with available ones: %s",
                "; ".join(errors)
            )
