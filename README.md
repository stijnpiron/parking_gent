# Parking Gent
![image](https://s3-eu-central-1.amazonaws.com/aws-ec2-eu-central-1-opendatasoft-staticfileset/gent/logo?tstamp=157675090777) 

![GitHub Release](https://img.shields.io/github/v/release/stijnpiron/parking_gent)
[![Validate with hassfest](https://github.com/stijnpiron/parking_gent/actions/workflows/hassfest.yml/badge.svg)](https://github.com/stijnpiron/parking_gent/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/stijnpiron/parking_gent/actions/workflows/hacs_validator.yml/badge.svg)](https://github.com/stijnpiron/parking_gent/actions/workflows/hacs_validator.yml)

## Home Assistant Parking Gent Integration
A robust Home Assistant integration providing real-time parking availability data for Ghent's parking facilities. Monitor only the parking locations you care about with intelligent error handling and clean logging.

## ✨ Key Features

### 🎯 **Smart Parking Selection**
- **Choose Your Parkings**: Select only the parking locations you want to monitor during setup
- **Easy Management**: Change your selection anytime through the configuration UI
- **Automatic Discovery**: Integration finds all available parking locations automatically
- **Efficient Updates**: Only fetches data for your selected parkings

### 🛡️ **Robust & Reliable**
- **Graceful Degradation**: Works even when some parking APIs are temporarily unavailable
- **Smart Caching**: Uses cached data during API outages to maintain availability
- **Automatic Recovery**: Resumes normal operation when APIs come back online
- **Clean Logging**: Errors only show in debug mode to prevent log spam

### 🔧 **Easy Setup & Management**
- **UI Configuration**: Set up through Home Assistant's interface (no YAML required)
- **Live Updates**: Change parking selection without restarting
- **Status Monitoring**: Clear indication of API health and data freshness

## 🏠 Supported Parking Locations

### 🚗 Parking Garages (Currently Available)
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

### 🚌 P+R Parking Lots (API Currently Unavailable)
- P+R Bourgoyen
- P+R Gentbrugge Arsenaal
- P+R Oostakker
- P+R The Loop
- P+R Wondelgem

*Note: The P+R parking API is currently returning 404 errors. The integration will automatically include these locations when the API becomes available again.*

## 📊 Provided Data
Each parking sensor provides:
- **Parking name** - Display name of the location
- **Available spaces** - Current number of free parking spots
- **Total capacity** - Maximum number of parking spaces
- **Occupation** - Current usage percentage
- **Opening status** - Whether the location is currently open
- **Opening hours** - Schedule information
- **Location coordinates** - GPS coordinates for navigation
- **Information URL** - Link to more details about the location  
- **Last update** - Timestamp of the most recent data update

## 🚀 Installation

### Method 1: HACS (Recommended)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

1. Open HACS in Home Assistant
2. Go to Integrations
3. Click the three dots menu → Custom repositories
4. Add repository: `stijnpiron/parking_gent`
5. Category: Integration
6. Install "Parking Gent"
7. Restart Home Assistant

### Method 2: Manual Installation
1. Download the latest release
2. Copy the `custom_components/parking_gent` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## ⚙️ Configuration

### UI Setup (Recommended)
1. Go to **Configuration** → **Integrations**
2. Click **Add Integration**
3. Search for "Parking Gent"
4. Enter an integration name
5. Select which parking locations you want to monitor
6. Click **Submit**

### Changing Parking Selection
1. Go to **Configuration** → **Integrations**
2. Find "Parking Gent" and click **Configure**
3. Modify your parking selection
4. Click **Submit** - changes apply immediately

### Legacy YAML Configuration (Deprecated)
For backward compatibility, YAML configuration is still supported but not recommended:

```yaml
sensor:
  - platform: parking_gent
```

*Note: YAML configuration will create sensors for all available parkings and doesn't support the new selection features.*

## 🔧 Advanced Configuration

### Debug Logging
To see detailed API information and troubleshooting data:

1. Go to **Configuration** → **Logs**
2. Click **Set Level**
3. Enter: `custom_components.parking_gent`
4. Select **Debug**
5. Click **Set Level**

This will show detailed information about API requests, data processing, and any connection issues.

### API Status Monitoring
The integration automatically monitors API health:
- **Green**: All selected APIs working normally
- **Yellow**: Some APIs failed but integration continues with available data  
- **Red**: All APIs failed, using cached data if available

## 📱 Usage Examples
- [Plotting the sensors on a map](documentation/custom_map-card.md)
- [Navigating via a script to the selected parking](documentation/navigate_to_parking.md)

## 🛠️ Troubleshooting

### Common Issues

**Integration not loading:**
- Check if APIs are accessible by enabling debug logging
- Verify internet connectivity
- Try restarting Home Assistant

**Some parking sensors missing:**
- Check if you've selected those parkings in configuration
- Some APIs may be temporarily unavailable (this is normal)

**Sensors showing "unavailable":**
- This may indicate parking location is closed or API issues
- Check debug logs for detailed information
- Sensors will automatically recover when data becomes available

### Getting Help
1. Enable debug logging (see Advanced Configuration)
2. Check the logs for specific error messages
3. Open an issue on GitHub with:
   - Home Assistant version
   - Integration version  
   - Debug log excerpts
   - Description of the problem

## 🔄 Version History

### v1.5.0 (Latest)
- ✅ **NEW**: UI-based configuration with parking selection
- ✅ **NEW**: Options flow for changing parking selection  
- ✅ **IMPROVED**: Robust error handling with graceful degradation
- ✅ **IMPROVED**: Clean logging (debug mode only for details)
- ✅ **IMPROVED**: Smart caching and automatic recovery
- ✅ **FIXED**: ConfigEntryNotReady errors during setup

### Previous Versions
- v1.4.0: Config flow support and API validation
- v1.3.1: Basic API integration
- Earlier: Legacy YAML-only configuration

## 🤝 Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- City of Ghent for providing the open data APIs
- Home Assistant community for the excellent platform
- All contributors and users providing feedback
