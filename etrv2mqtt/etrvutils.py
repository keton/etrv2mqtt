import json
from dataclasses import dataclass

from libetrv.bluetooth import btle
from libetrv.device import eTRVDevice


@dataclass(repr=False)
class eTRVData:
    name: str
    battery: int
    room_temp: float
    set_point: float

    def __repr__(self):
        return json.dumps(self.__dict__)


class eTRVUtils:
    @staticmethod
    def create_device(address: str, key: bytes, retry_limit: int = 5) -> eTRVDevice:
        return eTRVDevice(address, secret=key, retry_limit=retry_limit)

    @staticmethod
    def read_device(device: eTRVDevice) -> eTRVData:
        return eTRVData(device.name, device.battery, device.temperature.room_temperature, device.temperature.set_point_temperature)

    @staticmethod
    def set_temperature(device: eTRVDevice, temperature: float):
        device.temperature.set_point_temperature = float(temperature)
