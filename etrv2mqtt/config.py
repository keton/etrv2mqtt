from importlib import resources as importlib_resources
import json
from jsonschema import ValidationError, validate

class _ThermostatConfig:
        def __init__(self, topic, address, secret_key):
            self.topic=topic
            self.address=address
            self.secret_key=secret_key

class _MQTTConfig:
    def __init__(self, server, port, base_topic, user=None, password=None):
        self.server=server
        self.port=port
        self.base_topic=base_topic
        self.user=user
        self.password=password

class Config:
    def __init__(self, filename:str):
        self._config_schema=json.load(importlib_resources.open_text('etrv2mqtt.schemas','config.schema.json'))

        with open(filename, 'r') as configfile:
            _config_json=json.load(configfile)
            validate(instance=_config_json, schema=self._config_schema)
        self._config_json=_config_json
        self.mqtt=_MQTTConfig(
            _config_json['mqtt']['server'],
            _config_json['mqtt']['port'],
            _config_json['mqtt']['base_topic'],
            _config_json['mqtt']['user'] if 'user' in _config_json['mqtt'].keys() else None,
            _config_json['mqtt']['password'] if 'password' in _config_json['mqtt'].keys() else None
        )
        self.retry_limit=_config_json['retry_limit']
        self.poll_interval=_config_json['poll_interval']
        self.thermostats={}
        for t in _config_json['thermostats']:
            self.thermostats[t['topic']]=_ThermostatConfig(t['topic'], t['address'], t['secret_key'])
