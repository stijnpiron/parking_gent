import logging
import requests
from typing import Any, Dict, Optional, Mapping
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed, CoordinatorEntity

from .constants import (
    SCAN_INTERVAL,
    FIELDS_GARAGE,
    # FIELDS_MOBI,
    FIELDS_PR,
    API_PARKING,
    API_PR,
    # API_MOBI,
    API_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

""" requests only fetch a subset of relevant data, more documentation via the url. """
""" the mobi endpoint is only used for 3 extra parking locations from interparking that are not available in the parking garage or p+r endpoints"""
PARKING_API_URLS = [
    {
        "documentationUrl": "https://data.stad.gent/explore/dataset/bezetting-parkeergarages-real-time/information/?sort=-occupation",
        "url": API_PARKING,
        "mapping": FIELDS_GARAGE,
        "name": "Parking Garages",
    },
    {
        "documentationUrl": "https://data.stad.gent/explore/dataset/real-time-bezetting-pr-gent/information/?sort=name",
        "url": API_PR,
        "mapping": FIELDS_PR,
        "name": "P+R Parking",
    },
    # {
    #     "documentationUrl": "https://data.stad.gent/explore/dataset/mobi-parkings/information/",
    #     "url": API_MOBI,
    #     "mapping": FIELDS_MOBI,
    #     "name": "Mobi Parkings",
    # },
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Parking Gent sensor platform."""
    
    # Get user's parking selection
    selected_parkings = config_entry.data.get("selected_parkings", [])
    
    coordinator = ParkingGentCoordinator(hass, selected_parkings)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        _LOGGER.error("Failed to fetch initial data: %s", err)
        # Don't raise here, let the coordinator handle retries
        # The sensors will show as unavailable until data is fetched
    
    sensors = []
    if coordinator.data:
        for parking_id, parking_data in coordinator.data.items():
            # Only create sensors for selected parkings
            if not selected_parkings or parking_id in selected_parkings:
                sensors.append(ParkingSensor(coordinator, parking_id, parking_data))
    
    async_add_entities(sensors)


class ParkingGentCoordinator(DataUpdateCoordinator):
    """Fetch and normalize parking data from Stad Gent API."""

    def __init__(self, hass, selected_parkings=None):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Parking Gent",
            update_interval=SCAN_INTERVAL,
        )
        self.hass = hass
        self.selected_parkings = selected_parkings or []
        self._last_successful_data = {}

    async def _async_update_data(self):
        """Fetch and normalize data from API."""
        data = {}
        failed_apis = []
        
        for api_config in PARKING_API_URLS:
            try:
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug("Fetching data from %s API: %s", api_config["name"], api_config["url"])
                
                response = await self.hass.async_add_executor_job(
                    self._fetch_api_data, api_config["url"]
                )
                
                api_data = response.json()
                
                # Validate response structure
                if "results" not in api_data:
                    raise ValueError(f"API response missing 'results' field")
                
                results = api_data.get("results", [])
                if not results:
                    if _LOGGER.isEnabledFor(logging.DEBUG):
                        _LOGGER.debug("No results returned from %s API", api_config["name"])
                    continue
                
                # Process records
                processed_count = 0
                for record in results:
                    try:
                        normalized_record = self._normalize_record(
                            record, api_config["mapping"]
                        )
                        parking_id = normalized_record.get("name")
                        if parking_id:
                            # Only include selected parkings if filter is set
                            if not self.selected_parkings or parking_id in self.selected_parkings:
                                data[parking_id] = normalized_record
                                processed_count += 1
                        else:
                            if _LOGGER.isEnabledFor(logging.DEBUG):
                                _LOGGER.debug("Record missing name field in %s API", api_config["name"])
                    except Exception as err:
                        if _LOGGER.isEnabledFor(logging.DEBUG):
                            _LOGGER.debug(
                                "Failed to normalize record from %s API: %s", 
                                api_config["name"], err
                            )
                        continue
                
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug("Successfully processed %d/%d records from %s API", 
                                  processed_count, len(results), api_config["name"])
                
            except requests.exceptions.Timeout:
                error_msg = f"Timeout connecting to {api_config['name']} API"
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug(error_msg)
                failed_apis.append(error_msg)
            except requests.exceptions.ConnectionError:
                error_msg = f"Connection error to {api_config['name']} API"
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug(error_msg)
                failed_apis.append(error_msg)
            except requests.exceptions.HTTPError as err:
                error_msg = f"HTTP error from {api_config['name']} API: {err}"
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug(error_msg)
                failed_apis.append(error_msg)
            except ValueError as err:
                error_msg = f"Invalid response from {api_config['name']} API: {err}"
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug(error_msg)
                failed_apis.append(error_msg)
            except Exception as err:
                error_msg = f"Unexpected error from {api_config['name']} API: {err}"
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug(error_msg)
                failed_apis.append(error_msg)
        
        # If we got some data, update our successful data cache
        if data:
            self._last_successful_data = data
            if failed_apis and _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug(
                    "Partial data update successful (%d parking locations). Failed APIs: %s",
                    len(data), "; ".join(failed_apis)
                )
            elif _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug("Full data update successful (%d parking locations)", len(data))
            return data
        
        # If no new data but we have cached data, use that with a warning
        if self._last_successful_data:
            _LOGGER.warning(
                "All APIs failed, using cached data (%d parking locations)",
                len(self._last_successful_data)
            )
            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug("API errors: %s", "; ".join(failed_apis))
            return self._last_successful_data
        
        # If no data at all, raise UpdateFailed
        error_msg = f"All parking APIs failed and no cached data available"
        if _LOGGER.isEnabledFor(logging.DEBUG):
            error_msg += f": {'; '.join(failed_apis)}"
        _LOGGER.error(error_msg)
        raise UpdateFailed(error_msg)

    def _fetch_api_data(self, url: str):
        """Fetch data from API with timeout."""
        return requests.get(url, timeout=API_TIMEOUT)

    def _normalize_record(self, record, mapping):
        """Normalize the record based on the mapping."""
        normalized = {}
        for target_key, source_key in mapping.items():
            value = record.get(source_key)
            if value is not None:
                normalized[target_key] = value
            else:
                # Set default values for critical fields
                if target_key == "availableCapacity":
                    normalized[target_key] = 0
                elif target_key == "isOpenNow":
                    normalized[target_key] = False
                elif target_key == "totalCapacity":
                    normalized[target_key] = 0
                elif target_key == "occupation":
                    normalized[target_key] = 0
                else:
                    normalized[target_key] = None
                    
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    _LOGGER.debug("Missing field '%s' in record, using default value", source_key)
        
        return normalized


class ParkingSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Parking sensor."""

    def __init__(self, coordinator, parking_id, parking_data):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.parking_id = parking_id
        self._parking_data = parking_data
        self._attr_icon = "mdi:parking"
        self._attr_native_unit_of_measurement = "spaces"
        self._attr_unique_id = f"parking_{parking_id.lower().replace(' ', '_')}"
        self._attr_name = parking_data.get("name", parking_id)

    @property
    def native_value(self):
        """Return the state of the sensor (available capacity)."""
        if not self.coordinator.data:
            return None
        parking_data = self.coordinator.data.get(self.parking_id, {})
        return parking_data.get("availableCapacity", 0)

    @property
    def available(self):
        """Return True if the entity is available."""
        if not self.coordinator.last_update_success:
            return False
        parking_data = self.coordinator.data.get(self.parking_id, {})
        return bool(parking_data.get("isOpenNow", False))

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
            
        parking_data = self.coordinator.data.get(self.parking_id, {})
        
        # Safely extract location data
        location = parking_data.get("location", {})
        lat = None
        lon = None
        
        if isinstance(location, dict):
            lat = location.get("lat")
            lon = location.get("lon")
        
        return {
            "isOpenNow": bool(parking_data.get("isOpenNow", False)),
            "lastUpdate": parking_data.get("lastUpdate"),
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "occupation": parking_data.get("occupation", 0),
            "openingTimes": parking_data.get("openingTimes"),
            "totalCapacity": parking_data.get("totalCapacity", 0),
            "url": parking_data.get("url"),
        }
