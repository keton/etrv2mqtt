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
    hass_birth_topic: str
    hass_birth_payload: str

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
        validator_class, {"properties": set_defaults},
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
            _config_json['mqtt']['user'] if 'user' in _config_json['mqtt'].keys(
            ) else None,
            _config_json['mqtt']['password'] if 'password' in _config_json['mqtt'].keys(
            ) else None,
            _config_json['mqtt']['autodiscovery'],
            _config_json['mqtt']['autodiscovery_topic'],
            _config_json['mqtt']['autodiscovery_retain'],
            _config_json['mqtt']['hass_birth_topic'],
            _config_json['mqtt']['hass_birth_payload'],
        )
        self.retry_limit: int = _config_json['options']['retry_limit']
        self.poll_schedule: str = _config_json['options']['poll_schedule']
        self.poll_interval: int = _config_json['options']['poll_interval']
        self.poll_hour_minute: int = _config_json['options']['poll_hour_minute']
        self.stay_connected: bool = _config_json['options']['stay_connected']
        self.report_room_temperature: bool = _config_json['options']['report_room_temperature']
        self.setpoint_debounce_time: int = _config_json['options']['setpoint_debounce_time']
        self.thermostats: Dict[str, ThermostatConfig] = {}

        for t in _config_json['thermostats']:
            if t['topic'] in self.thermostats.keys():
                raise ValueError("Duplicate thermostat topic: "+t['topic'])

            self.thermostats[t['topic']] = ThermostatConfig(
                t['topic'],
                t['address'],
                t['secret_key']
            )
