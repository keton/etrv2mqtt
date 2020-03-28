import json
from dataclasses import dataclass
from importlib import resources as importlib_resources

from jsonschema import validate
from typing import Dict, Optional


@dataclass
class ThermostatConfig:
    topic: str
    address: str
    secret_key: str


@dataclass
class _MQTTConfig:
    server: str
    port: int
    base_topic: str
    user: Optional[str]
    password: Optional[str]
    autodiscovery: bool
    autodiscovery_topic: str
    autodiscovery_retain: bool

class Config:
    def __init__(self, filename: str):
        _config_schema = json.load(importlib_resources.open_text(
            'etrv2mqtt.schemas', 'config.schema.json'))

        with open(filename, 'r') as configfile:
            _config_json = json.load(configfile)
            validate(instance=_config_json, schema=_config_schema)

        self.mqtt = _MQTTConfig(
            _config_json['mqtt']['server'],
            _config_json['mqtt']['port'],
            _config_json['mqtt']['base_topic'],
            _config_json['mqtt']['user'] if 'user' in _config_json['mqtt'].keys() else None,
            _config_json['mqtt']['password'] if 'password' in _config_json['mqtt'].keys() else None,
            _config_json['mqtt']['autodiscovery'],
            _config_json['mqtt']['autodiscovery_topic'] if 'autodiscovery_topic' in _config_json['mqtt'].keys() else 'homeassistant',
            _config_json['mqtt']['autodiscovery_retain'] if 'autodiscovery_retain' in _config_json['mqtt'].keys() else True
        )
        self.retry_limit:int = _config_json['retry_limit']
        self.poll_interval:int = _config_json['poll_interval']
        self.stay_connected = _config_json['stay_connected'] if 'stay_connected' in _config_json.keys() else False
        self.thermostats:Dict[str, ThermostatConfig] = {}
        for t in _config_json['thermostats']:
            self.thermostats[t['topic']] = ThermostatConfig(
                t['topic'],
                t['address'],
                t['secret_key']
            )
