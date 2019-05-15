"""
Read temperature information from RuuviTag beacons.

Sample config:

sensor:
  - platform: ruuvitag
    beacons:
      living_room:
        mac: "AA:BB:CC:DD:EE:FF"

Installation
------------

Copy sensor.py to <homeassistanconf>/custom_components/ruuvitag/
Uses ruuvitag_sensor plugin as dependency so works perfectly only on Linux and expects 
that hcidump and hcitool are installed.

Version
-------
1.0     25.06.2018     First release.
1.1     05.05.2019     Updated structure for new integration

Created by
----------
Petri Suutarinen-Maaheimo
petri.suutarinen@gmail.com

Greetings
---------
Code is inspired by Home Assistant official sensor plugins (eddystonebeacon and skybeacon) with own twist.

"""

import logging
import time
import threading

import voluptuous as vol

from ruuvitag_sensor.ruuvi import RuuviTagSensor

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, TEMP_CELSIUS, STATE_UNKNOWN, EVENT_HOMEASSISTANT_STOP,
    EVENT_HOMEASSISTANT_START)

REQUIREMENTS = ['ruuvitag_sensor==0.11.0', 'construct==2.9.41']

_LOGGER = logging.getLogger(__name__)

CONF_BEACONS = 'beacons'
CONF_MAC = 'mac'

ATTR_DEVICE = 'device'
ATTR_MODEL = 'model'

BEACON_SCHEMA = vol.Schema({
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_NAME): cv.string
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_BEACONS): vol.Schema({cv.string: BEACON_SCHEMA}),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Validate configuration, create devices and start monitoring thread."""

    beacons = config.get("beacons")
    devices = []

    for dev_name, properties in beacons.items():
        mac = get_from_conf(properties, "mac", 17)
        name = properties.get(CONF_NAME, dev_name)

        if mac is None:
            _LOGGER.error("Skipping %s", dev_name)
            continue
        else:
            devices.append(RuuvitagTemp(name + "_temperature", mac))
            devices.append(RuuvitagHumidity(name + "_humidity", mac))
            devices.append(RuuvitagPressure(name + "_pressure", mac))

    if devices:
        mon = Monitor(hass, devices)

        def monitor_stop(_service_or_event):
            """Stop the monitor thread."""
            _LOGGER.info("Stopping scanner for Ruuvitag beacons")
            mon.terminate()

        add_devices(devices)
        hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, monitor_stop)
        mon.start()
    else:
        _LOGGER.warning("No devices were added")


def get_from_conf(config, config_key, length):
    """Retrieve value from config and validate length."""
    string = config.get(config_key)
    if len(string) != length:
        _LOGGER.error("Error in config parameter %s: Must be exactly %d "
                      "bytes. Device will not be added", config_key, length/2)
        return None
    return string


class RuuvitagEntity(Entity):
    def __init__(self, name, mac):
        """Initialize a sensor."""
        self._name = name
        self.mac = mac

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name


    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            ATTR_DEVICE: "RuuviTag",
            ATTR_MODEL: 1,
        }

class RuuvitagTemp(RuuvitagEntity):
    """Representation of a temperature sensor."""

    def __init__(self, name, mac):
        """Initialize a sensor."""
        super(RuuvitagTemp, self).__init__(name, mac)
        self.data = { 'temperature' : STATE_UNKNOWN }

    @property
    def state(self):
        """Return the state of the device."""
        return self.data['temperature']

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return TEMP_CELSIUS

class RuuvitagHumidity(RuuvitagEntity):
    """Representation of a humidity sensor."""

    def __init__(self, name, mac):
        """Initialize a sensor."""
        super(RuuvitagHumidity, self).__init__(name, mac)
        self.data = { 'humidity' : STATE_UNKNOWN }

    @property
    def state(self):
        """Return the state of the device."""
        return self.data['humidity']

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return "%"

class RuuvitagPressure(RuuvitagEntity):
    """Representation of a atmospheric pressure sensor."""

    def __init__(self, name, mac):
        """Initialize a sensor."""
        super(RuuvitagPressure, self).__init__(name, mac)
        self.data = { 'pressure' : STATE_UNKNOWN }

    @property
    def state(self):
        """Return the state of the device."""
        return self.data['pressure']

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return "hPa"

class Monitor(threading.Thread):
    """Continuously scan for BLE advertisements."""

    def __init__(self, hass, devices):
        """Construct interface object."""
        threading.Thread.__init__(self)
        self.daemon = False
        self.keep_going = threading.Event()

        self.hass = hass
        self.devices = devices

    def run(self):
        """Continuously scan for BLE advertisements."""

        macs = set(map(lambda x : x.mac,  self.devices))

        while not self.keep_going.wait(10):
            items = RuuviTagSensor.get_data_for_sensors(macs)
            self.process_packet(items)

    def process_packet(self, items):
        """Assign temperature to device."""
        for dev in self.devices:
            if dev.mac in items:
                data = items[dev.mac]
                dev.data = data
                dev.schedule_update_ha_state()

    def terminate(self):
        """Signal runner to stop and join thread."""
        self.keep_going.set()
        self.join()