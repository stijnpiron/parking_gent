# Navigate to parking script
When setting a tap_action on the map-card component, this is an example of a script that will show a notification on your mobile device.\
When the notification is tapped, it will launch Waze (must be installed) and start navigating to the selected parking.

```yaml
alias: Navigate to Location
description: Start Waze navigation to a specific location directly
fields:
  entity_id:
    selector:
      entity: {}
    name: Entity ID
sequence:
  - variables:
      latitude: "{{ state_attr(entity_id, 'latitude') }}"
      longitude: "{{ state_attr(entity_id, 'longitude') }}"
      location: "{{ state_attr(entity_id, 'friendly_name') }}"
  - data:
      message: "Navigate to: {{ location }}"
      data:
        url: |
          waze://?ll={{ latitude | float }},{{ longitude | float }}&navigate=yes
    action: notify.notify
```

Other navigation applications are also possible, just need to replace the url with the appropriate one for the other navigation application.