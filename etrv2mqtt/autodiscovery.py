import copy
import json
from dataclasses import dataclass
from etrv2mqtt.config import Config


@dataclass
class AutodiscoveryResult():
    topic: str
    payload: str

class Autodiscovery():
    
    _termostat_template = json.loads("""
    {
        "~": "etrv/kitchen",
        "name":"Kitchen",
        "unique_id":"0000_thermostat",
        "temp_cmd_t":"~/set",
        "temp_stat_t":"~/state",
        "temp_stat_tpl":"{{ value_json.set_point }}",
        "curr_temp_t":"~/state",
        "curr_temp_tpl":"{{ value_json.room_temp }}",
        "min_temp":"10",
        "max_temp":"30",
        "temp_step":"0.5",
        "modes":["heat"],
        "send_if_off": true,
        "device": {
            "identifiers":"0000",
            "manufacturer": "Danfoss",
            "model": "eTRV"
        }
    }
    """)

    _battery_template = json.loads("""
    {
        "device_class": "battery",
        "name": "kitchen battery",
        "unique_id":"0000_battery",
        "state_topic": "etrv/kitchen/state",
        "value_template": "{{ value_json.battery }}",
        "unit_of_measurement": "%",
        "device": {
            "identifiers":"0000",
            "manufacturer": "Danfoss",
            "model": "eTRV"
        }
    }
    """)

    _reported_name_template = json.loads("""
    {
        "name": "kitchen reported name",
        "unique_id":"0000_rep_name",
        "state_topic": "etrv/kitchen/state",
        "value_template": "{{ value_json.name }}",
        "device": {
            "identifiers":"0000",
            "manufacturer": "Danfoss",
            "model": "eTRV"
        }
    }
    """)
    
    def __init__(self, config:Config):
        self._config=config
    
    def _autodiscovery_topic(self, dev_mac:str, entity_class:str, entity_type: str)->str:
        return '/'.join((
            self._config.mqtt.autodiscovery_topic,
            entity_class,
            self._config.mqtt.base_topic,
            dev_mac.replace(':', '_')+'_'+entity_type,
            'config'
        ))
    
    def _autodiscovery_payload(self, template:dict, dev_mac:str, dev_name:str, sensor_name: str)->dict:
        payload = copy.deepcopy(template)
        payload['name'] = dev_name+' '+sensor_name
        payload['unique_id'] = dev_mac.replace(':', '_')+'_'+sensor_name.lower().replace(' ','_')
        payload['device']['name'] = dev_name
        payload['device']['identifiers'] = dev_mac
        return payload

    def register_termostat(self, dev_name: str, dev_mac: str)->AutodiscoveryResult:
        autodiscovery_topic = self._autodiscovery_topic(dev_mac, 'climate', 'thermostat')
        
        autodiscovery_msg=self._autodiscovery_payload(self._termostat_template, dev_mac, dev_name, "Thermostat")
        autodiscovery_msg['~'] = self._config.mqtt.base_topic+'/'+dev_name

        return AutodiscoveryResult(autodiscovery_topic, payload=json.dumps(autodiscovery_msg))

    def register_battery(self, dev_name: str, dev_mac: str)->AutodiscoveryResult:
        autodiscovery_topic = self._autodiscovery_topic(dev_mac, 'sensor', 'battery')
        
        autodiscovery_msg=self._autodiscovery_payload(self._battery_template, dev_mac, dev_name, "Battery")
        autodiscovery_msg['state_topic'] = '/'.join(( 
            self._config.mqtt.base_topic,
            dev_name,
            'state'
        ))
        return AutodiscoveryResult(autodiscovery_topic, payload=json.dumps(autodiscovery_msg))

    def register_reported_name(self, dev_name: str, dev_mac: str)->AutodiscoveryResult:
        autodiscovery_topic = self._autodiscovery_topic(dev_mac, 'sensor', 'rep_name')
        
        autodiscovery_msg=self._autodiscovery_payload(self._reported_name_template, dev_mac, dev_name, "Reported name")
        autodiscovery_msg['state_topic'] = '/'.join(( 
            self._config.mqtt.base_topic,
            dev_name,
            'state'
        ))
        return AutodiscoveryResult(autodiscovery_topic, payload=json.dumps(autodiscovery_msg))

