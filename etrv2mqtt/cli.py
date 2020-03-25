import sys

from loguru import logger

from etrv2mqtt.config import Config
from etrv2mqtt.devices import DeviceManager, TRVDevice


def main(config_file: str):
    try:
        config = Config(config_file)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    
    deviceManager=DeviceManager(config, TRVDevice)
    deviceManager.poll_forever()

def usage():
    print('Usage: '+sys.argv[0]+' configfile.json')
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
    else:
        main(sys.argv[1])
