from datetime import timedelta

# Constants for API configurations
BASE_API_URL = "https://data.stad.gent/api/explore"
API_VERSION = "v2.1"

DATASET_GARAGE = "bezetting-parkeergarages-real-time"
DATASET_PR = "real-time-bezetting-pr-gent"
DATASET_MOBI = "mobi-parkings"

FIELDS_GARAGE = {
    "availableCapacity": "availablecapacity",
    "isOpenNow": "isopennow",
    "lastUpdate": "lastupdate",
    "location": "location",
    "name": "name",
    "occupation": "occupation",
    "openingTimes": "openingtimesdescription",
    "totalCapacity": "totalcapacity",
    "url": "urllinkaddress",
}
FIELDS_PR = {
    "availableCapacity": "availablespaces",
    "isOpenNow": "isopennow",
    "lastUpdate": "lastupdate",
    "location": "location",
    "name": "name",
    "occupation": "occupation",
    "openingTimes": "openingtimesdescription",
    "totalCapacity": "numberofspaces",
    "url": "urllinkaddress",
}
FIELDS_MOBI = {
    "availableCapacity": "availablecapacity",
    "isOpenNow": "isopennow",
    "lastUpdate": "lastupdate",
    "location": "location",
    "name": "id_parking",
    "occupation": "occupation",
    "openingTimes": "openingtimesdescription",
    "totalCapacity": "totalcapacity",
    "url": "urllinkaddress",
}

PARKING_SELECT_MOBI = [
    "Interparking Zuid",
    "Interparking Kouter",
    "Interparking Center",
]

SCAN_INTERVAL = timedelta(minutes=5)


def compose_select(mapping):
    return ",".join(mapping.values())


def join_array(elements):
    return ",".join([f'"{element}"' for element in elements])


API_PARKING = f"{BASE_API_URL}/{API_VERSION}/catalog/datasets/{DATASET_GARAGE}/records?select={compose_select(FIELDS_GARAGE)}&limit=100"
API_PR = f"{BASE_API_URL}/{API_VERSION}/catalog/datasets/{DATASET_PR}/records?select={compose_select(FIELDS_PR)}&limit=100"
API_MOBI = f'{BASE_API_URL}/{API_VERSION}/catalog/datasets/{DATASET_MOBI}/records?select={compose_select(FIELDS_MOBI)}&where={FIELDS_MOBI["totalCapacity"]} > 0 and id_parking IN ({join_array(PARKING_SELECT_MOBI)})&limit=100'
