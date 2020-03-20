from loguru import logger
import paho.mqtt.client as paho_mqtt
from libetrv.device import eTRVDevice

from etrv2mqtt.config import Config
from typing import Dict, Callable


class Mqtt(object):
    def __init__(self, config: Config, devices: Dict[str, eTRVDevice], set_temperature_callback: Callable[[Dict[str, eTRVDevice], str, float], None]):
        self._config = config
        self._devices = devices
        self._set_temperature_callback = set_temperature_callback

        self._client = paho_mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        if config.mqtt.user is not None:
            self._client.username_pw_set(
                config.mqtt.user, password=config.mqtt.password)
        logger.debug("connecting to {}:{}",
                     config.mqtt.server, config.mqtt.port)
        self._client.connect_async(config.mqtt.server, port=config.mqtt.port)
        self._client.loop_start()

    def publish_device_data(self, name: str, data: str):
        if self._client.is_connected():
            self._client.publish(
                self._config.mqtt.base_topic+'/'+name+'/data', payload=data)

    def _on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code "+str(rc))
        self._client.subscribe(
            self._config.mqtt.base_topic+'/+/set_temperature')

    def _on_message(self, client, userdata, msg):
        logger.info("on_message: "+msg.topic+" "+str(msg.payload))
        name = msg.topic.split('/')[-2]
        logger.debug('device name:'+name)
        if name in self._devices.keys():
            try:
                self._set_temperature_callback(
                    self._devices, name, float(msg.payload))
            except ValueError:
                logger.debug("{} is not a valid float", msg.payload)
