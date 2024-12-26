import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ParkingAPIHealthCheck")

# Parking API URLs
PARKING_API_URLS = [
    {
        "name": "Parking Garages",
        "url": "https://data.stad.gent/api/explore/v2.1/catalog/datasets/bezetting-parkeergarages-real-time/records?select=name,totalcapacity,availablecapacity,occupation,openingtimesdescription,isopennow,location,urllinkaddress,lastupdate&limit=100",
        "expected_fields": ["name","totalcapacity","availablecapacity","occupation","openingtimesdescription","isopennow","location","urllinkaddress"]
    },
    {
        "name": "P+R Parking",
        "url": "https://data.stad.gent/api/explore/v2.1/catalog/datasets/real-time-bezetting-pr-gent/records?select=name,numberofspaces,availablespaces,occupation,openingtimesdescription,isopennow,location,urllinkaddress,lastupdate&limit=100",
        "expected_fields": ["name","numberofspaces","availablespaces","occupation","openingtimesdescription","isopennow","location","urllinkaddress"]
    },
    {
        "name": "Mobi Parkings",
        "url": "https://data.stad.gent/api/explore/v2.1/catalog/datasets/mobi-parkings/records?select=id_parking,totalcapacity,availablecapacity,occupation,openingtimesdescription,isopennow,location,urllinkaddress,lastupdate&where=totalcapacity > 0 and id_parking IN (\"Interparking Zuid\", \"Interparking Kouter\", \"Interparking Center\")&limit=100",
        "expected_fields": ["id_parking","totalcapacity","availablecapacity","occupation","openingtimesdescription","isopennow","location","urllinkaddress","lastupdate"]
    },
]

def check_api(api_config):
    """Check an API for available fields."""
    url = api_config["url"]
    name = api_config["name"]
    expected_fields=api_config["expected_fields"]

    try:
        logger.info(f"Starting check for API: \"{name}\"")
        response = requests.get(url)
        response.raise_for_status()

        data = response.json().get("results", [])
        if not data:
            logger.warning(f"No data found for API: \"{name}\"")
            logger.error(f"API \"{name}\": FAILED - Empty response data")
            return False

        all_fields_found = True

        # Validate fields in each record
        for i, record in enumerate(data):
            missing_fields = [field for field in expected_fields if field not in record]
            if missing_fields:
                all_fields_found = False
                logger.error(f"Record {i} in API \"{name}\": Missing fields {missing_fields}")
            else:
                logger.info(f"Record {i} in API \"{name}\": PASSED - All fields found")

        if all_fields_found:
            logger.info(f"API \"{name}\": PASSED - All records have expected fields")
            return True
        else:
            logger.error(f"API \"{name}\": FAILED - One or more records have missing fields")
            return False

    except Exception as e:
        logger.error(f"API \"{name}\": FAILED - Error occurred: {e}")
        return False


def main():
    all_passed = True

    for api in PARKING_API_URLS:
        result = check_api(api)
        if result:
            logger.info(f"API \"{api['name']}\": SUCCESS")
        else:
            logger.error(f"API \"{api['name']}\": FAILURE")
            all_passed = False

    if all_passed:
        logger.info("All APIs passed successfully!")
        exit(0)
    else:
        logger.error("One or more APIs failed. Check logs for details.")
        exit(1)


if __name__ == "__main__":
    main()
