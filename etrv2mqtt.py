#!/usr/bin/env python3

import sys
sys.path.insert(1, '/home/hass/libetrv')

from libetrv.cli import Device
from libetrv.bluetooth import btle
from loguru import logger

def create_device(address:str, key:bytes) -> Device:
    return Device(address, None, key, retry_limit=5)

def read_device(device: Device) -> dict:
    d=device._device
    return {'name': d.name, 'battery': d.battery, 'room_temp': d.temperature.room_temperature, 'set_point': d.temperature.set_point_temperature}

def set_temperature(device: Device, temperature: float):
    device.set_setpoint(float(temperature))

def main(device_mac, device_key):
    try:
        device = create_device(device_mac, bytes.fromhex(device_key))
        ret = read_device(device)
        print(ret)
    except btle.BTLEDisconnectError as e:
        logger.error(e)

if __name__ == "__main__":
   main(sys.argv[1], sys.argv[2])

