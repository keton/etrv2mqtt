from libetrv.device import eTRVDevice
from libetrv.bluetooth import btle
from dataclasses import dataclass,asdict


@dataclass(repr=False)
class eTRVData:
    name: str
    battery: int
    room_temp: float
    set_point: float

    def __repr__(self):
        return str(asdict(self))


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
