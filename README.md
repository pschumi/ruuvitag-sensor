# ruuvitag-sensor
Sensor plugin for home assistant.

Read temperature, humidity and atmospheric pressure information from RuuviTag beacons. So far this should work on all Linux based machines with bluez kernel module support. Sensor component uses ruuvitag-sensor library to read values.

## Installation:
Copy ruuvitag.py to your .homeassistant/custom_components/sensor/ -directory.

Ensure that hcidump and hcitool are installed on the host machine.

For Home Assistant running in a virtual environment you have to install the ruuvitag package inside the virtual environment:

1. Change user to homeassistant and activate virtual environment and install ruuvitag-sensor:
```
$ sudo -u homeassistant -H -s
$ source /srv/homeassistant/bin/activate
$ pip3 install ruuvitag-sensor
$ exit
```

2. Add permissions to homeassistant user with "sudo visudo":
```
homeassistant   ALL = (ALL) NOPASSWD: /bin/hciconfig, /usr/bin/hcitool, /usr/bin/hciattach, /usr/bin/hcidump, /usr/bin/hcitool, /bin/kill
```


## Configuration:
configuration.yml

    sensor:
      - platform: ruuvitag
        beacons:
          living_room:
            mac: "AA:BB:CC:DD:EE:FF"
          other_room:
            mac: "BB:AA:CC:DD:EE:FF"

