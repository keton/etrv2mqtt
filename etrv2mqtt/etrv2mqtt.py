#!/usr/bin/env python3

import sys
from libetrv.device import eTRVDevice
from libetrv.bluetooth import btle
from loguru import logger

from etrv2mqtt.etrvutils import eTRVUtils

def main(device_mac, device_key):
    try:
        device = eTRVUtils.create_device(device_mac, bytes.fromhex(device_key))
        ret = eTRVUtils.read_device(device)
        print(ret)
    except btle.BTLEDisconnectError as e:
        logger.error(e)

if __name__ == "__main__":
   main(sys.argv[1], sys.argv[2])

