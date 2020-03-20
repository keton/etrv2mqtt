from libetrv.device import eTRVDevice
from libetrv.bluetooth import btle

class eTRVUtils:
    @staticmethod
    def create_device(address:str, key:bytes) -> eTRVDevice:
        return eTRVDevice(address, secret=key, retry_limit=5)
    
    @staticmethod
    def read_device(device: eTRVDevice) -> dict:
        return {'name': device.name, 'battery': device.battery, 'room_temp': device.temperature.room_temperature, 'set_point': device.temperature.set_point_temperature}

    @staticmethod
    def set_temperature(device: eTRVDevice, temperature: float):
        device.temperature.set_point_temperature=float(temperature)
