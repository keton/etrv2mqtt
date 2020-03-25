from dataclasses import dataclass, asdict
from etrv2mqtt.mqtt import Mqtt
from etrv2mqtt.devices import DeviceBase
from etrv2mqtt.config import ThermostatConfig, Config
from etrv2mqtt.etrvutils import eTRVData
from loguru import logger

@dataclass
class _eTRVDummyDevice:
    name: str
    address: str
    secret_key: bytes
    battery: int = 99
    set_point: float = 21
    current_temp: float = 21

class DummyDevice(DeviceBase):
    def __init__(self, thermostat_config:ThermostatConfig, config:Config):
        super().__init__(thermostat_config, config)
        self._device=_eTRVDummyDevice(thermostat_config.topic, thermostat_config.address, bytes.fromhex(thermostat_config.secret_key))

    def poll(self, mqtt:Mqtt):
        logger.debug("Polling data from {}", self._device.name)
        ret = eTRVData(self._device.name, self._device.battery, self._device.current_temp, self._device.set_point)
        logger.debug(str(ret))
        mqtt.publish_device_data(self._device.name, str(ret))
        
    def set_temperature(self, mqtt:Mqtt, temperature: float):
        logger.debug("Setting {} to {}C", self._device.name, temperature)
        self._device.set_point=temperature
        self.poll(mqtt)
    
