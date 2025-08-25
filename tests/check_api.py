import logging
import requests
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../custom_components/parking_gent")
    ),
)

from constants import (
    API_PARKING,
    API_PR,
    # API_MOBI,
    FIELDS_GARAGE,
    # FIELDS_MOBI,
    FIELDS_PR,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ParkingAPIHealthCheck")

# Parking API URLs - P+R API temporarily disabled due to 404 errors
PARKING_PROPS = [
    {
        "name": "Parking Garages",
        "url": API_PARKING,
        "expected_fields": list(FIELDS_GARAGE.values()),
        "expected_parkings": [
            "Vrijdagmarkt",
            "Sint-Michiels",
            "Tolhuis",
            "Ledeberg",
            "The Loop",
            "Reep",
            "Ramen",
            "B-Park Gent Sint-Pieters",
            "Dok noord",
            "Savaanstraat",
            "Sint-Pietersplein",
            "Getouw",
            "B-Park Dampoort",
        ],
    },
    # P+R API temporarily disabled due to 404 errors from City of Gent
    # Will be re-enabled when the endpoint is fixed
    # {
    #     "name": "P+R Parking",
    #     "url": API_PR,
    #     "expected_fields": list(FIELDS_PR.values()),
    #     "expected_parkings": [
    #         "P+R Wondelgem",
    #         "P+R The Loop",
    #         "P+R Oostakker",
    #         "P+R Gentbrugge Arsenaal",
    #         "P+R Bourgoyen",
    #     ],
    # },
    # {
    #     "name": "Mobi Parkings",
    #     "url": API_MOBI,
    #     "expected_fields": list(FIELDS_MOBI.values()),
    #     "expected_parkings": [
    #         "Interparking Center",
    #         "Interparking Kouter",
    #         "Interparking Zuid",
    #     ],
    # },
]


def check_api(api_config):
    """Check an API for available fields."""
    url = api_config["url"]
    name = api_config["name"]
    expected_fields = api_config["expected_fields"]
    expected_parkings = api_config["expected_parkings"]

    try:
        logger.info(f'Starting check for API: "{name}"')
        logger.info(f'Composed endpoint: "{url}"')
        response = requests.get(url)
        response.raise_for_status()

        # Parse response JSON
        response_json = response.json()
        data = response_json.get("results", [])
        total_count = response_json.get("total_count")

        # Validate total_count matches length of data
        if total_count is not None and total_count != len(expected_parkings):
            logger.error(
                f'API "{name}": FAILED - "total_count" ({total_count}) does not match length of data ({len(expected_parkings)})'
            )
            all_parkings_found = False

        if not data:
            logger.warning(f'No data found for API: "{name}"')
            logger.error(f'API "{name}": FAILED - Empty response data')
            all_parkings_found = False

        all_fields_found = True
        all_parkings_found = True

        # Verify expected parkings are in the response
        response_parking_names = {
            record.get("name") or record.get("id_parking") for record in data
        }
        missing_parkings = [
            parking
            for parking in expected_parkings
            if parking not in response_parking_names
        ]

        if missing_parkings:
            all_parkings_found = False
            logger.error(
                f'API "{name}": FAILED - Missing expected parkings: {missing_parkings}'
            )
        else:
            logger.info(f'API "{name}": PASSED - All expected parkings are present')

        # Validate fields in each record
        for i, record in enumerate(data):
            missing_fields = [field for field in expected_fields if field not in record]
            parking_name = record.get("name") or record.get("id_parking")
            if missing_fields:
                all_fields_found = False
                logger.error(
                    f'Record {i} in API "{name}": Missing fields {missing_fields} for parking "{parking_name}"'
                )
            else:
                logger.info(
                    f'Record {i} in API "{name}": PASSED - All fields found for parking "{parking_name}"'
                )

        # Final decision based on the checks
        if all_fields_found and all_parkings_found:
            logger.info(f'API "{name}": PASSED - All records have expected fields')
            return True
        else:
            logger.error(
                f'API "{name}": FAILED - One or more records have missing fields'
            )
            return False

    except Exception as e:
        logger.error(f'API "{name}": FAILED - Error occurred: {e}')
        return False


def main():
    all_passed = True

    for api in PARKING_PROPS:
        result = check_api(api)
        if result:
            logger.info(f'API "{api['name']}": SUCCESS')
        else:
            logger.error(f'API "{api['name']}": FAILURE')
            all_passed = False

    if all_passed:
        logger.info("All APIs passed successfully!")
        exit(0)
    else:
        logger.error("One or more APIs failed. Check logs for details.")
        exit(1)


if __name__ == "__main__":
    main()
