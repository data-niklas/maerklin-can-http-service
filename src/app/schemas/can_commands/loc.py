from enum import Enum

from .base import AbstractCANMessage
from ..can import CommandSchema
from ...utils.coding import int_to_bytes

class AbstractLocIDCommand(AbstractCANMessage):
    loc_id: int

    def get_other_data(self) -> bytes:
        raise NotImplentedError()

    def get_data(self) -> bytes:
        data = bytes()
        data += int_to_bytes(self.loc_id, 4)
        data += self.get_other_data()
        return data

class LocomotiveSpeedCommand(AbstractLocIDCommand):
    speed: int = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.LocomotiveSpeed
    
    def get_other_data(self) -> bytes:
        if self.speed is None:
            assert not self.response
            return bytes()
        assert self.speed <= 1000
        return int_to_bytes(self.speed, 2)

class LocomotiveDirection(str, Enum):
    Keep = "Keep"
    Forwards = "Forwards"
    Backwards = "Backwards"
    Toggle = "Toggle"

class LocomotiveDirectionCommand(AbstractLocIDCommand):
    direction: LocomotiveDirection = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.LocomotiveDirection
    
    def get_other_data(self) -> bytes:
        if self.direction is None:
            assert not self.response
            return bytes()
        if self.direction == LocomotiveDirection.Keep:
            return int_to_bytes(0, 1)
        if self.direction == LocomotiveDirection.Forwards:
            return int_to_bytes(1, 1)
        if self.direction == LocomotiveDirection.Backwards:
            return int_to_bytes(2, 1)
        if self.direction == LocomotiveDirection.Toggle:
            return int_to_bytes(3, 1)

class LocomotiveFunctionCommand(AbstractLocIDCommand):
    function: int
    value: int = None
    function_value: int = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.LocomotiveFunction
    
    def get_other_data(self) -> bytes:
        ret = bytes()

        ret += int_to_bytes(self.function, 1)
        if self.value is not None:
            ret += int_to_bytes(self.value, 1)
        else:
            assert self.function_value is None
        if self.function_value is not None:
            ret += int_to_bytes(self.function_value, 2)

        return ret

class ReadConfigCommand(AbstractLocIDCommand):
    index: int # 6 bit
    number: int # 10 bit
    count: int = None
    value: int = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.ReadConfig
    
    def get_other_data(self) -> bytes:
        ret = bytes()

        byte4 = self.index << 2
        byte4 |= (self.number >> 8) & 0b0000_0011
        ret += int_to_bytes(byte4, 1)
        ret += int_to_bytes(self.number & 0b11111111, 1)

        if self.count is not None:
            assert self.value is None
            ret += int_to_bytes(self.count, 1)
        elif self.value is not None:
            assert self.count is None
            ret += int_to_bytes(self.value, 1)
        return ret


class SwitchingAccessoriesCommand(AbstractLocIDCommand):
    position: int
    power: int
    value: int = None # time or special value. Time: t*10 ms


    def get_command(self) -> CommandSchema:
        return CommandSchema.SwitchingAccessories
    
    def get_other_data(self) -> bytes:
        ret = bytes()
        ret += int_to_bytes(self.position, 1)
        ret += int_to_bytes(self.power, 1)
        if self.value is not None:
            ret += int_to_bytes(self.value, 2)
        return ret
