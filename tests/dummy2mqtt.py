import sys

from loguru import logger

from etrv2mqtt.config import Config
from etrv2mqtt.devices import DeviceManager
from tests.dummyDevice import DummyDevice


def main(config_file: str):
    try:
        config = Config(config_file)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    
    deviceManager=DeviceManager(config, DummyDevice)
    deviceManager.poll_forever()

def entrypoint():
    if len(sys.argv) < 2:
        print('Usage: '+sys.argv[0]+' configfile.json')
        sys.exit(0)
    else:
        main(sys.argv[1])

if __name__ == "__main__":
    entrypoint()
