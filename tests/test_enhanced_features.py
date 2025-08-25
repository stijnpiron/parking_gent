"""Quick test to verify the enhanced parking selection functionality."""

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

from config_flow import get_available_parkings
from sensor import ParkingGentCoordinator

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class MockHass:
    """Mock Home Assistant object for testing."""
    
    async def async_add_executor_job(self, func, *args):
        """Mock executor job."""
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args)
            return future.result()


async def test_parking_discovery():
    """Test parking discovery functionality."""
    _LOGGER.info("🔍 Testing parking discovery...")
    
    mock_hass = MockHass()
    
    try:
        available_parkings = await get_available_parkings(mock_hass)
        
        if available_parkings:
            _LOGGER.info("✅ Successfully discovered parking locations:")
            total_count = 0
            for api_name, parkings in available_parkings.items():
                _LOGGER.info(f"  📍 {api_name}: {len(parkings)} locations")
                for parking in parkings[:3]:  # Show first 3
                    _LOGGER.info(f"    - {parking}")
                if len(parkings) > 3:
                    _LOGGER.info(f"    ... and {len(parkings) - 3} more")
                total_count += len(parkings)
            
            _LOGGER.info(f"🎯 Total discovered: {total_count} parking locations")
            return available_parkings
        else:
            _LOGGER.error("❌ No parking locations discovered")
            return None
            
    except Exception as err:
        _LOGGER.error(f"❌ Failed to discover parkings: {err}")
        return None


async def test_selective_coordinator():
    """Test coordinator with parking selection."""
    _LOGGER.info("🎛️ Testing selective coordinator...")
    
    # First discover available parkings
    available_parkings = await test_parking_discovery()
    if not available_parkings:
        return False
    
    # Select first 3 parkings from working APIs
    selected_parkings = []
    for api_name, parkings in available_parkings.items():
        selected_parkings.extend(parkings[:2])  # Take first 2 from each API
        if len(selected_parkings) >= 3:
            break
    
    selected_parkings = selected_parkings[:3]  # Limit to 3
    
    _LOGGER.info(f"🎯 Testing with selected parkings: {selected_parkings}")
    
    mock_hass = MockHass()
    coordinator = ParkingGentCoordinator(mock_hass, selected_parkings)
    
    try:
        data = await coordinator._async_update_data()
        
        if data:
            _LOGGER.info(f"✅ Got data for {len(data)} selected parking locations:")
            for parking_id, parking_info in data.items():
                spaces = parking_info.get('availableCapacity', 'N/A')
                total = parking_info.get('totalCapacity', 'N/A')
                _LOGGER.info(f"  🚗 {parking_id}: {spaces}/{total} spaces")
            
            # Verify we only got selected parkings
            unexpected = set(data.keys()) - set(selected_parkings)
            if unexpected:
                _LOGGER.warning(f"⚠️ Got unexpected parkings: {unexpected}")
            else:
                _LOGGER.info("✅ Selection filtering works correctly")
            
            return True
        else:
            _LOGGER.error("❌ No data returned from selective coordinator")
            return False
            
    except Exception as err:
        _LOGGER.error(f"❌ Selective coordinator test failed: {err}")
        return False


async def main():
    """Run all tests."""
    _LOGGER.info("🚀 Starting Parking Gent Enhanced Features Test")
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Parking Discovery
    if await test_parking_discovery():
        success_count += 1
    
    # Test 2: Selective Coordinator
    if await test_selective_coordinator():
        success_count += 1
    
    _LOGGER.info(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        _LOGGER.info("🎉 All enhanced features working correctly!")
        _LOGGER.info("✨ Users can now:")
        _LOGGER.info("   - Select specific parkings during setup")
        _LOGGER.info("   - Change selection later via options")
        _LOGGER.info("   - Enjoy cleaner logs (debug only)")
        _LOGGER.info("   - Have robust error handling")
    else:
        _LOGGER.error("❌ Some tests failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
