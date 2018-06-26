# ruuvitag-sensor
Sensor plugin for home assistant.

Read temperature, humidity and atmospheric pressure information from RuuviTag beacons. So far this should work on all Linux based machines with bluez kernel module support. Sensor component uses ruuvitag-sensor library to read values.

## Installation:
Copy ruuvitag.py to your .homeassistant/custom_components/sensor/ -directory.

Ensure that hcidump and hcitool are installed on the host machine.


## Configuration:
configuration.yml

    sensor:
      - platform: ruuvitag
        beacons:
          living_room:
            mac: "AA:BB:CC:DD:EE:FF"
          other_room:
            mac: "BB:AA:CC:DD:EE:FF"

