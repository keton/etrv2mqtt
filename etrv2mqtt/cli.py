#!/usr/bin/env python3

import sys
from libetrv.bluetooth import btle
from loguru import logger

from etrv2mqtt.etrvutils import eTRVUtils
from etrv2mqtt.config import Config

import time

devices={}
config={}

def poll_devices(devices:dict):
    for name,device in devices.items():
        try:
            logger.debug("Polling data from {}",name)
            ret = eTRVUtils.read_device(device)
            logger.info(str(ret))
        except btle.BTLEDisconnectError as e:
            logger.error(e)

def set_temperature_callback(devices:dict, name:str, temperature:float):
    if name not in devices.keys():
        logger.warning("Attempting to set temperature for non existing device {}", name)
        return
    try:
        logger.debug("Setting {} to {}C", name, temperature)
        device=devices[name]
        eTRVUtils.set_temperature(device, temperature)
    except btle.BTLEDisconnectError as e:
        logger.error(e)

def main(config_file:str):
    try:
        config=Config(config_file)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    
    for thermostat_config in config.thermostats.values():
            logger.debug("Adding {} MAC: {} key: {}",thermostat_config.topic, thermostat_config.address, thermostat_config.secret_key)
            device = eTRVUtils.create_device(thermostat_config.address, bytes.fromhex(thermostat_config.secret_key), retry_limit=config.retry_limit)
            devices[thermostat_config.topic]=device

    while True:
        poll_devices(devices)
        time.sleep(config.poll_interval)
            
if __name__ == "__main__":
   main(sys.argv[1])