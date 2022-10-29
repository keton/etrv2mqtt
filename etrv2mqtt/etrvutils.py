import json
import enum
from dataclasses import dataclass

from libetrv.device import eTRVDevice
from libetrv.data_struct import ScheduleMode
from datetime import datetime

class PresetModes(enum.Enum):
    Manual = ScheduleMode.MANUAL
    Scheduled = ScheduleMode.SCHEDULED
    Vacation = ScheduleMode.VACATION

@dataclass(repr=False)
class eTRVData:
    name: str
    battery: int
    room_temp: float
    set_point: float
    preset_mode: str
    last_update: datetime

    def _datetimeconverter(self, o):
        if isinstance(o, datetime):
            return o.astimezone().isoformat()
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
        mode: str
        try:
            mode = PresetModes(device.settings.schedule_mode).name
        except ValueError:
            mode = "None"

        return eTRVData(device.name,
                        device.battery,
                        device.temperature.room_temperature,
                        device.temperature.set_point_temperature,
                        mode,
                        datetime.now())

    @staticmethod
    def set_temperature(device: eTRVDevice, temperature: float):
        device.temperature.set_point_temperature = float(temperature)

    @staticmethod
    def set_mode(device: eTRVDevice, mode: bytes):
        device.settings.schedule_mode = PresetModes[mode.decode('utf-8')].value
        device.settings.save()
