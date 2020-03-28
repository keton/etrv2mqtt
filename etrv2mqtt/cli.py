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

@logger.catch
def entrypoint():
    if len(sys.argv) < 2:
        logger.error('Usage: '+sys.argv[0]+' configfile.json')
        sys.exit(0)
    else:
        logger.info(sys.argv[0] + ' is starting')
        main(sys.argv[1])

if __name__ == "__main__":
    entrypoint()
