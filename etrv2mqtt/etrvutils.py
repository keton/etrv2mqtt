import json
from dataclasses import dataclass

from libetrv.bluetooth import btle
from libetrv.device import eTRVDevice
from datetime import datetime

@dataclass(repr=False)
class eTRVData:
    name: str
    battery: int
    room_temp: float
    set_point: float
    last_update: datetime

    def _datetimeconverter(self, o):
        if isinstance(o, datetime):
            return o.__str__()
        else: 
            return o

    def __repr__(self):
        return json.dumps(self.__dict__, default=self._datetimeconverter)


class eTRVUtils:
    @staticmethod
    def create_device(address: str, key: bytes, retry_limit: int = 5) -> eTRVDevice:
        return eTRVDevice(address, secret=key, retry_limit=retry_limit)

    @staticmethod
    def read_device(device: eTRVDevice) -> eTRVData:
        return eTRVData(device.name, device.battery, device.temperature.room_temperature, device.temperature.set_point_temperature, datetime.now())

    @staticmethod
    def set_temperature(device: eTRVDevice, temperature: float):
        device.temperature.set_point_temperature = float(temperature)
