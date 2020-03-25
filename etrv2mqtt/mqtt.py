from __future__ import annotations

from loguru import logger
import paho.mqtt.client as paho_mqtt
from libetrv.device import eTRVDevice

from etrv2mqtt.config import Config
from etrv2mqtt.autodiscovery import Autodiscovery, AutodiscoveryResult
from typing import Dict, Callable

import json
import copy


class Mqtt(object):

    _is_connected: bool = False

    def is_connected(self) -> bool:
        return self._is_connected

    def __init__(self, config: Config, devices: Dict[str, eTRVDevice],
                 set_temperature_callback: Callable[[Mqtt, Dict[str, eTRVDevice], str, float], None] = None,
                 on_connect_callback: Callable[[Mqtt, Dict[str, eTRVDevice]], None] = None):
        self._config = config
        self._devices = devices
        self._set_temperature_callback = set_temperature_callback
        self._on_connect_callback = on_connect_callback

        self._client = paho_mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
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
                self._config.mqtt.base_topic+'/'+name+'/state', payload=data)

    def _publish_autodiscovery_result(self, result: AutodiscoveryResult, retain: bool = False):
        self._client.publish(
            result.topic, payload=result.payload, retain=retain)

    def _on_connect(self, client, userdata, flags, rc):
        logger.info("Connected to MQTT server")
        if self._config.mqtt.autodiscovery:
            ad = Autodiscovery(self._config)
            for thermostat in self._config.thermostats.values():
                self._publish_autodiscovery_result(ad.register_termostat(
                    thermostat.topic, thermostat.address), self._config.mqtt.autodiscovery_retain)
                self._publish_autodiscovery_result(ad.register_battery(
                    thermostat.topic, thermostat.address), self._config.mqtt.autodiscovery_retain)
                self._publish_autodiscovery_result(ad.register_reported_name(
                    thermostat.topic, thermostat.address), self._config.mqtt.autodiscovery_retain)

        self._client.subscribe(
            self._config.mqtt.base_topic+'/+/set')

        if self._on_connect_callback is not None:
            self._on_connect_callback(self._devices)

        self._is_connected = True

    def _on_disconnect(self, client, userdata, rc):
        logger.debug("disconnected from mqtt server")
        self._is_connected = False

    def _on_message(self, client, userdata, msg):
        logger.debug("on_message: "+msg.topic+" "+str(msg.payload))
        name = msg.topic.split('/')[-2]
        if name in self._devices.keys():
            try:
                if self._set_temperature_callback is not None:
                    self._set_temperature_callback(
                        self, self._devices, name, float(msg.payload))
            except ValueError:
                logger.debug("{} is not a valid float", msg.payload)

    @property
    def set_temperature_callback(self) -> Callable[[Mqtt, Dict[str, eTRVDevice], str, float], None]:
        return self._set_temperature_callback

    @set_temperature_callback.setter
    def set_temperature_callback(self, callback: Callable[[Mqtt, Dict[str, eTRVDevice], str, float], None]):
        self._set_temperature_callback = callback
