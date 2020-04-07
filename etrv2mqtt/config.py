import json
from dataclasses import dataclass
from importlib import resources as importlib_resources

from jsonschema import validate, Draft7Validator, validators
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

# from https://python-jsonschema.readthedocs.io/en/stable/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance
def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )

class Config:
    def __init__(self, filename: str):
        _config_schema = json.load(importlib_resources.open_text(
            'etrv2mqtt.schemas', 'config.schema.json'))

        with open(filename, 'r') as configfile:
            _config_json = json.load(configfile)
        
        # apply config schema defaults if values are missing
        DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)
        DefaultValidatingDraft7Validator(_config_schema).validate(_config_json)

        self.mqtt = _MQTTConfig(
            _config_json['mqtt']['server'],
            _config_json['mqtt']['port'],
            _config_json['mqtt']['base_topic'],
            _config_json['mqtt']['user'] if 'user' in _config_json['mqtt'].keys() else None,
            _config_json['mqtt']['password'] if 'password' in _config_json['mqtt'].keys() else None,
            _config_json['mqtt']['autodiscovery'],
            _config_json['mqtt']['autodiscovery_topic'],
            _config_json['mqtt']['autodiscovery_retain']
        )
        self.retry_limit:int = _config_json['retry_limit']
        self.poll_interval:int = _config_json['poll_interval']
        self.stay_connected:bool = _config_json['stay_connected']
        self.report_room_temperature:bool = _config_json['report_room_temperature']
        self.setpoint_debounce_time:int = _config_json['setpoint_debounce_time']
        self.thermostats:Dict[str, ThermostatConfig] = {}
        
        for t in _config_json['thermostats']:
            self.thermostats[t['topic']] = ThermostatConfig(
                t['topic'],
                t['address'],
                t['secret_key']
            )
