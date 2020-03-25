from loguru import logger
import paho.mqtt.client as paho_mqtt
from libetrv.device import eTRVDevice

from etrv2mqtt.config import Config
from typing import Dict, Callable

import json
import copy

class Mqtt(object):

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

    _is_connected:bool=False

    def _autodiscovery_register_termostat(self, dev_name:str, dev_mac:str, retain:bool=True):
        autodiscovery_topic=self._config.mqtt.autodiscovery_topic+'/'+'climate'+'/'+self._config.mqtt.base_topic+'/'+dev_mac.replace(':', '_')+'_thermostat'+'/config'
        autodiscovery_msg=copy.deepcopy(self._termostat_template)
        autodiscovery_msg['name']=dev_name
        autodiscovery_msg['unique_id']=dev_mac.replace(':', '_')+'_thermostat'
        autodiscovery_msg['~']=self._config.mqtt.base_topic+'/'+dev_name
        autodiscovery_msg['device']['name']=dev_name
        autodiscovery_msg['device']['identifiers']=dev_mac
        self._client.publish(autodiscovery_topic, payload=json.dumps(autodiscovery_msg), retain=retain)

    def _autodiscovery_register_battery(self, dev_name:str, dev_mac:str, retain:bool=True):
        autodiscovery_topic=self._config.mqtt.autodiscovery_topic+'/'+'sensor'+'/'+self._config.mqtt.base_topic+'/'+dev_mac.replace(':', '_')+'_battery'+'/config'
        autodiscovery_msg=copy.deepcopy(self._battery_template)
        autodiscovery_msg['name']=dev_name+' battery'
        autodiscovery_msg['unique_id']=dev_mac.replace(':', '_')+'_battery'
        autodiscovery_msg['state_topic']=self._config.mqtt.base_topic+'/'+dev_name+'/state'
        autodiscovery_msg['device']['name']=dev_name
        autodiscovery_msg['device']['identifiers']=dev_mac
        self._client.publish(autodiscovery_topic, payload=json.dumps(autodiscovery_msg), retain=retain)

    def _autodiscovery_register_reported_name(self, dev_name:str, dev_mac:str, retain:bool=True):
        autodiscovery_topic=self._config.mqtt.autodiscovery_topic+'/'+'sensor'+'/'+self._config.mqtt.base_topic+'/'+dev_mac.replace(':', '_')+'_rep_name'+'/config'
        autodiscovery_msg=copy.deepcopy(self._reported_name_template)
        autodiscovery_msg['name']=dev_name+' reported name'
        autodiscovery_msg['unique_id']=dev_mac.replace(':', '_')+'_rep_name'
        autodiscovery_msg['state_topic']=self._config.mqtt.base_topic+'/'+dev_name+'/state'
        autodiscovery_msg['device']['name']=dev_name
        autodiscovery_msg['device']['identifiers']=dev_mac
        self._client.publish(autodiscovery_topic, payload=json.dumps(autodiscovery_msg), retain=retain)

    def is_connected(self)->bool:
        return self._is_connected

    def __init__(self, config: Config, devices: Dict[str, eTRVDevice], 
                    set_temperature_callback: Callable[[Dict[str, eTRVDevice], str, float], None], 
                    on_connect_callback: Callable[[Dict[str, eTRVDevice]], None]=None):
        self._config = config
        self._devices = devices
        self._set_temperature_callback = set_temperature_callback
        self._on_connect_callback=on_connect_callback

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

    def _on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code "+str(rc))
        if self._config.mqtt.autodiscovery:
            for thermostat in self._config.thermostats.values():
                self._autodiscovery_register_termostat(thermostat.topic, thermostat.address, self._config.mqtt.autodiscovery_retain)
                self._autodiscovery_register_battery(thermostat.topic, thermostat.address, self._config.mqtt.autodiscovery_retain)
                self._autodiscovery_register_reported_name(thermostat.topic, thermostat.address, self._config.mqtt.autodiscovery_retain)

        self._client.subscribe(
            self._config.mqtt.base_topic+'/+/set')
        
        if self._on_connect_callback is not None:
            self._on_connect_callback(self._devices)

        self._is_connected=True
    
    def _on_disconnect(self, client, userdata, rc):
        logger.debug("disconnected from mqtt server")
        self._is_connected=False

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
