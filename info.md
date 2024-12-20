# Parking Gent
![image](https://s3-eu-central-1.amazonaws.com/aws-ec2-eu-central-1-opendatasoft-staticfileset/gent/logo?tstamp=157675090777) 

## Home Assistant parking Gent integration.
Provides realtime overview of available parking spots in the Ghent parking lots and P+R locations.

## Supported parking lots and garages

### Parking garages/lots
- B-Park Dampoort
- B-Park Gent Sint-Pieters
- Dok noord
- Getouw
- Interparking Center
- Interparking Kouter
- Interparking Zuid
- Ledeberg
- Ramen
- Reep
- Savaanstraat
- Sint-Michiels
- Sint-Pietersplein
- The Loop
- Tolhuis
- Vrijdagmarkt
- 
### P+R parking lots
- P+R Bourgoyen
- P+R Gentbrugge Arsenaal
- P+R Oostakker
- P+R The Loop
- P+R Wondelgem

## Provided data
- Parking name
- Total parking spaces
- Available parking spaces
- Occupied places
- Opening time schedule
- Wether the location is currently open or not
- Location coordinates
- Url for more information about the location
- Timestamp when the last data update was done for the location

## How to
### Installations via HACS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

- In HACS, look for "ghent parking" and install and restart
  - If integration was not found, please add custom repository `stijnpiron/parking_gent` as integration
- add the config to the `configuration.yaml` file:
```
sensor:
  - platform: parking_gent
```

