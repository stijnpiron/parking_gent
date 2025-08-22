# Parking Gent
![image](https://s3-eu-central-1.amazonaws.com/aws-ec2-eu-central-1-opendatasoft-staticfileset/gent/logo?tstamp=157675090777) 

![GitHub Release](https://img.shields.io/github/v/release/stijnpiron/parking_gent)
[![Validate with hassfest](https://github.com/stijnpiron/parking_gent/actions/workflows/hassfest.yml/badge.svg)](https://github.com/stijnpiron/parking_gent/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/stijnpiron/parking_gent/actions/workflows/hacs_validator.yml/badge.svg)](https://github.com/stijnpiron/parking_gent/actions/workflows/hacs_validator.yml)

## Home Assistant Parking Gent Integration

Provides real-time overview of available parking spots in Ghent parking garages and P+R locations with robust error handling and user-friendly setup.

### ✨ Key Features

- 🎯 **User-Selectable Parkings**: Choose which parking locations to monitor during setup
- 🔧 **Easy Configuration**: UI-based setup with options to modify selection later
- 🛡️ **Robust Error Handling**: Continues working even when some APIs are unavailable
- 📊 **Smart Logging**: Clean logs with debug-only detailed information
- ⚡ **Efficient**: Only fetches data for selected parking locations
- 🔄 **Auto-Recovery**: Automatically resumes when APIs come back online

## Current API Status

✅ **Parking Garages API**: Fully operational (13 locations)  
⏸️ **P+R Parking API**: Temporarily disabled due to City of Gent API issues (404 errors)

*The P+R API has been temporarily disabled to ensure clean integration operation. It will be automatically re-enabled when the City of Gent fixes their API endpoint.*

## Supported Parking Locations

### 🏢 Parking Garages (Currently Available)
- B-Park Dampoort
- B-Park Gent Sint-Pieters  
- Dok noord
- Getouw
- Ledeberg
- Ramen
- Reep
- Savaanstraat
- Sint-Michiels
- Sint-Pietersplein
- The Loop
- Tolhuis
- Vrijdagmarkt

### 🚗 P+R Parking Lots (Temporarily Disabled)
- P+R Bourgoyen
- P+R Gentbrugge Arsenaal
- P+R Oostakker
- P+R The Loop
- P+R Wondelgem

*P+R locations are temporarily disabled due to City of Gent API issues. They will be automatically re-enabled when the API is restored.*

## Provided Data
- Parking name
- Total parking spaces
- Available parking spaces  
- Occupied places
- Opening time schedule
- Whether the location is currently open or not
- Location coordinates
- URL for more information about the location
- Timestamp when the last data update was done for the location

## Installation

### Via HACS (Recommended)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

1. Look for `Parking Gent` in HACS integrations
2. If not found, add as custom repository: `stijnpiron/parking_gent`
3. Install the integration
4. Restart Home Assistant
5. Add integration via UI: **Configuration** → **Integrations** → **Add Integration** → **Parking Gent**

### Manual Installation
1. Copy the `custom_components/parking_gent` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant  
3. Add integration via UI: **Configuration** → **Integrations** → **Add Integration** → **Parking Gent**

## Configuration

### UI Setup (Recommended)
1. Go to **Configuration** → **Integrations** → **Add Integration**
2. Search for **Parking Gent** and select it
3. Enter an integration name
4. Select which parking locations you want to monitor
5. Click **Submit** - sensors will be created for your selected parkings

### Changing Parking Selection
1. Go to **Configuration** → **Integrations**
2. Find **Parking Gent** and click **Configure**  
3. Modify your parking selection
4. Click **Submit** - changes apply immediately

### Legacy Configuration (Deprecated)
For backward compatibility, the old `configuration.yaml` method still works:

```yaml
sensor:
  - platform: parking_gent
```

*Note: This method monitors all available parkings and doesn't provide selection options.*

## Troubleshooting

### Debug Logging
If you experience issues, enable debug logging:

1. Go to **Configuration** → **Logs**
2. Set level for `custom_components.parking_gent` to **Debug**
3. Check logs for detailed API and processing information

### Common Issues
- **No sensors created**: Ensure at least one parking location is selected during setup
- **Sensors show unavailable**: Check if the parking location is currently open
- **Integration won't load**: Check debug logs for API connectivity issues

## API Status Check
The integration includes API health monitoring. Check the logs for current API status or run the test script in the `tests/` directory.

## Examples
- [Plotting the sensors on a map](documentation/custom_map-card.md)
- [Navigating via a script to the selected parking](documentation/navigate_to_parking.md)

## Version History

### v1.5.0 - Enhanced User Experience
- Added user-selectable parking locations
- Implemented UI-based configuration with options flow
- Enhanced error handling and logging
- Improved API robustness and caching
- Added graceful degradation for partial API failures

### v1.4.0 - Robustness Improvements  
- Fixed ConfigEntryNotReady errors
- Added proper config entry setup
- Enhanced error handling for API failures

### Previous Versions
- See [release history](https://github.com/stijnpiron/parking_gent/releases) for details
