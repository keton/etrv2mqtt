from etrv2mqtt.config import Config
from etrv2mqtt.etrvutils import eTRVData
from etrv2mqtt.mqtt import Mqtt
from loguru import logger
from typing import Dict
from dataclasses import dataclass, asdict
import sys
import time


@dataclass
class _eTRVDummyDevice:
    name: str
    address: str
    secret_key: bytes
    battery: int = 99
    set_point: float = 21
    current_temp: float = 21

mqtt: Mqtt

def set_temperature_callback(devices: Dict[str, _eTRVDummyDevice], name: str, temperature: float):
    if name not in devices.keys():
        logger.warning(
            "Attempting to set temperature for non existing device {}", name)
        return
    logger.debug("Setting {} to {}C", name, temperature)
    device = devices[name]
    device.set_point=temperature
    # Home assistant needs to see updated temperature value to confirm change
    poll_device(devices, name)

def poll_device(devices: Dict[str, _eTRVDummyDevice], name: str):
    device = devices[name]
    logger.debug("Polling data from {}", name)
    ret = eTRVData(device.name, device.battery, device.current_temp, device.set_point)
    logger.debug(str(ret))
    mqtt.publish_device_data(name, str(ret))

def poll_devices(devices: Dict[str, _eTRVDummyDevice]):
    for name in devices.keys():
        poll_device(devices, name)

def main(config_file: str):
    try:
        config = Config(config_file)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    devices:Dict[str, _eTRVDummyDevice]={}

    for thermostat_config in config.thermostats.values():
        logger.debug("Adding {} MAC: {} key: {}", thermostat_config.topic, thermostat_config.address, thermostat_config.secret_key)
        device = _eTRVDummyDevice(thermostat_config.topic, thermostat_config.address, bytes.fromhex(thermostat_config.secret_key))
        devices[thermostat_config.topic] = device

    global mqtt
    mqtt = Mqtt(config, devices, set_temperature_callback)

    while True:
        if mqtt.is_connected():
            poll_devices(devices)
            time.sleep(config.poll_interval)
        else:
            time.sleep(2)


def usage():
    print('Usage: '+sys.argv[0]+' configfile.json')
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
    else:
        main(sys.argv[1])
