from __future__ import annotations

from typing import Callable, Dict

import paho.mqtt.client as paho_mqtt
from loguru import logger

from .autodiscovery import Autodiscovery, AutodiscoveryResult
from .config import Config


class Mqtt(object):

    _is_connected: bool = False

    def is_connected(self) -> bool:
        return self._is_connected

    def __init__(self, config: Config):
        self._config = config

        self._client = paho_mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        if config.mqtt.user is not None:
            self._client.username_pw_set(
                config.mqtt.user, password=config.mqtt.password)
        logger.debug("connecting to {}:{}",
                     config.mqtt.server, config.mqtt.port)

        self._client.will_set(self._config.mqtt.base_topic +
                              '/state', 'offline', retain=True)
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

        self._client.publish(self._config.mqtt.base_topic +
                             '/state', 'online', retain=True)

        if self._config.mqtt.autodiscovery:
            ad = Autodiscovery(self._config)
            for thermostat in self._config.thermostats.values():
                self._publish_autodiscovery_result(ad.register_termostat(
                    thermostat.topic, thermostat.address), self._config.mqtt.autodiscovery_retain)
                self._publish_autodiscovery_result(ad.register_battery(
                    thermostat.topic, thermostat.address), self._config.mqtt.autodiscovery_retain)
                self._publish_autodiscovery_result(ad.register_reported_name(
                    thermostat.topic, thermostat.address), self._config.mqtt.autodiscovery_retain)
                if self._config.report_room_temperature:
                    self._publish_autodiscovery_result(ad.register_room_temperature(
                        thermostat.topic, thermostat.address), self._config.mqtt.autodiscovery_retain)
                self._publish_autodiscovery_result(ad.register_last_update_timestamp(
                    thermostat.topic, thermostat.address), self._config.mqtt.autodiscovery_retain)

        # subscribe to set temperature topics
        self._client.subscribe(
            self._config.mqtt.base_topic+'/+/set')

        # subscribe to Home Assistant birth topic
        self._client.subscribe(self._config.mqtt.hass_birth_topic)

        self._is_connected = True

    def _on_disconnect(self, client, userdata, rc):
        logger.debug("disconnected from mqtt server")
        self._is_connected = False

    def _on_message(self, client, userdata, msg):
        # hass birth message
        if msg.topic == self._config.mqtt.hass_birth_topic:
            try:
                # MQTT payload can be random bytes
                payload_str = msg.payload.decode("utf-8")
                if payload_str == self._config.mqtt.hass_birth_payload and self._hass_birth_callback is not None:
                    self._hass_birth_callback(self)
            except UnicodeError:
                pass

        # thermostat set temperature message
        elif msg.topic.startswith(self._config.mqtt.base_topic) and msg.topic.endswith('/set'):
            name = msg.topic.split('/')[-2]
            try:
                if self._set_temperature_callback is not None:
                    self._set_temperature_callback(
                        self, name, float(msg.payload))
            except ValueError:
                logger.warning("{}: {} is not a valid float",
                               name, msg.payload)

    @property
    def set_temperature_callback(self) -> Callable[[Mqtt, str, float], None]:
        return self._set_temperature_callback

    @set_temperature_callback.setter
    def set_temperature_callback(self, callback: Callable[[Mqtt, str, float], None]):
        self._set_temperature_callback = callback

    @property
    def hass_birth_callback(self) -> Callable[[Mqtt], None]:
        return self._hass_birth_callback

    @hass_birth_callback.setter
    def hass_birth_callback(self, callback: Callable[[Mqtt], None]):
        self._hass_birth_callback = callback
