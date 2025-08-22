"""Test script to verify the robustness of the parking integration."""

import asyncio
import logging
import sys
import os

# Add the custom components directory to the path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../custom_components/parking_gent")
    ),
)

from sensor import ParkingGentCoordinator

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class MockHass:
    """Mock Home Assistant object for testing."""
    
    async def async_add_executor_job(self, func, *args):
        """Mock executor job."""
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args)
            return future.result()


async def test_coordinator_robustness():
    """Test that the coordinator handles API failures gracefully."""
    _LOGGER.info("Testing coordinator robustness...")
    
    mock_hass = MockHass()
    coordinator = ParkingGentCoordinator(mock_hass)
    
    try:
        # This should succeed partially (parking garages work, P+R fails)
        data = await coordinator._async_update_data()
        
        if data:
            _LOGGER.info(f"SUCCESS: Got data for {len(data)} parking locations:")
            for parking_id, parking_info in data.items():
                _LOGGER.info(f"  - {parking_id}: {parking_info.get('availableCapacity', 'N/A')} spaces available")
            
            # Check if we have parking garage data
            garage_found = any("garage" in str(parking_info).lower() or 
                             parking_id in ['Savaanstraat', 'Reep', 'Sint-Pietersplein', 'The Loop', 'Vrijdagmarkt', 
                                          'Sint-Michiels', 'Ramen', 'B-Park Gent Sint-Pieters', 'B-Park Dampoort', 
                                          'Tolhuis', 'Ledeberg', 'Getouw', 'Dok noord']
                             for parking_id, parking_info in data.items())
            
            if garage_found:
                _LOGGER.info("SUCCESS: Parking garage data found despite P+R API failure")
                return True
            else:
                _LOGGER.error("FAILED: No expected parking garage data found")
                return False
        else:
            _LOGGER.error("FAILED: No data returned")
            return False
            
    except Exception as err:
        _LOGGER.error(f"FAILED: Exception occurred: {err}")
        return False


async def main():
    """Run the test."""
    success = await test_coordinator_robustness()
    
    if success:
        _LOGGER.info("✅ Integration robustness test PASSED")
        _LOGGER.info("The integration can handle partial API failures and continue working")
    else:
        _LOGGER.error("❌ Integration robustness test FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
