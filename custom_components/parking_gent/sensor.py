import logging
import requests
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


""" requests only fetch a subset of relevant data, more documentation via the url. """
""" the mobi endpoint is only used for 3 extra parking locations that are not available in the parking garage or p+r endpoints"""
PARKING_API_URLS = [
    {
        "documentationUrl":"https://data.stad.gent/explore/dataset/bezetting-parkeergarages-real-time/information/?sort=-occupation",
        "url": "https://data.stad.gent/api/explore/v2.1/catalog/datasets/bezetting-parkeergarages-real-time/records?select=name,totalcapacity,availablecapacity,occupation,openingtimesdescription,isopennow,location,urllinkaddress,lastupdate&limit=100",
        "mapping": {
            "availableCapacity": "availablecapacity",
            "isOpenNow": "isopennow",
            "lastUpdate": "lastupdate",
            "location": "location",
            "name": "name",
            "occupation": "occupation",
            "openingTimes": "openingtimesdescription",
            "totalCapacity": "totalcapacity",
            "url": "urllinkaddress",
        },
    },
    {
        "documentationUrl":"https://data.stad.gent/explore/dataset/real-time-bezetting-pr-gent/information/?sort=name",
        "url": "https://data.stad.gent/api/explore/v2.1/catalog/datasets/real-time-bezetting-pr-gent/records?select=name,numberofspaces,availablespaces,occupation,openingtimesdescription,isopennow,location,urllinkaddress,lastupdate&limit=100",
        "mapping": {
            "availableCapacity": "availablespaces",
            "isOpenNow": "isopennow",
            "lastUpdate": "lastupdate",
            "location": "location",
            "name": "name",
            "occupation": "occupation",
            "openingTimes": "openingtimesdescription",
            "totalCapacity": "numberofspaces",
            "url": "urllinkaddress",
        },
    },
    {
        "documentationUrl":"https://data.stad.gent/explore/dataset/mobi-parkings/information/",
        "url": "https://data.stad.gent/api/explore/v2.1/catalog/datasets/mobi-parkings/records?select=id_parking,totalcapacity,availablecapacity,occupation,openingtimesdescription,isopennow,location,urllinkaddress,lastupdate&where=totalcapacity > 0 and id_parking IN (\"Interparking Zuid\", \"Interparking Kouter\", \"Interparking Center\")&limit=100",
        "mapping": {
            "availableCapacity": "availablecapacity",
            "isOpenNow": "isopennow",
            "lastUpdate": "lastupdate",
            "location": "location",
            "name": "id_parking",
            "occupation": "occupation",
            "openingTimes": "openingtimesdescription",
            "totalCapacity": "totalcapacity",
            "url": "urllinkaddress",
        },
    },
]

SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Parking Gent sensor platform."""
    coordinator = ParkingGentCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for parking_id, parking_data in coordinator.data.items():
        sensors.append(ParkingSensor(coordinator, parking_id, parking_data))

    async_add_entities(sensors)


class ParkingGentCoordinator(DataUpdateCoordinator):
    """Fetch and normalize parking data from Stad Gent API."""

    def __init__(self, hass):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Parking Gent",
            update_interval=SCAN_INTERVAL,
        )
        self.hass = hass

    async def _async_update_data(self):
        """Fetch and normalize data from API."""
        try:
            data = {}
            for api_config in PARKING_API_URLS:
                response = await self.hass.async_add_executor_job(requests.get, api_config["url"])
                response.raise_for_status()
                api_data = response.json()
                for record in api_data.get("results", []):
                    normalized_record = self._normalize_record(record, api_config["mapping"])
                    parking_id = normalized_record["name"]
                    data[parking_id] = normalized_record
            return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

    def _normalize_record(self, record, mapping):
        """Normalize the record based on the mapping."""
        normalized = {}
        for target_key, source_key in mapping.items():
            normalized[target_key] = record.get(source_key)
        return normalized


class ParkingSensor(SensorEntity):
    """Representation of a Parking sensor."""

    def __init__(self, coordinator, parking_id, parking_data):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.parking_id = parking_id
        self.parking_data = parking_data

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.parking_data["name"]

    @property
    def state(self):
        """Return the state of the sensor (available capacity)."""
        return self.parking_data["availableCapacity"]

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "isOpenNow": bool(self.parking_data["isOpenNow"]),
            "lastUpdate": self.parking_data["lastUpdate"],
            "location": self.parking_data["location"],
            "occupation": self.parking_data["occupation"],
            "openingTimes": self.parking_data["openingTimes"],
            "totalCapacity": self.parking_data["totalCapacity"],
            "url": self.parking_data["url"],
        }

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"parking_{self.parking_id.lower().replace(' ', '_')}"