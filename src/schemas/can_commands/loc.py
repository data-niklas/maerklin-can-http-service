from enum import Enum

from .base import AbstractCANMessage
from ..can import CommandSchema

class AbstractLocIDCommand(AbstractCANMessage):
    loc_id: int

    def get_other_data(self) -> bytes:
        raise NotImplentedError()

    def get_data(self) -> bytes:
        data = bytes()
        data += self.loc_id.to_bytes(4, "big")
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
        return self.speed.to_bytes(2, "big")

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
            return int(0).to_bytes(1, "big")
        if self.direction == LocomotiveDirection.Forwards:
            return int(1).to_bytes(1, "big")
        if self.direction == LocomotiveDirection.Backwards:
            return int(2).to_bytes(1, "big")
        if self.direction == LocomotiveDirection.Toggle:
            return int(3).to_bytes(1, "big")

class LocomotiveFunctionCommand(AbstractLocIDCommand):
    function: int
    value: int = None
    function_value: int = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.LocomotiveFunction
    
    def get_other_data(self) -> bytes:
        ret = bytes()

        ret += self.function.to_bytes(1, "big")
        if self.value is not None:
            ret += self.value.to_bytes(1, "big")
        else:
            assert self.function_value is None
        if self.function_value is not None:
            ret += self.function_value.to_bytes(2, "big")

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
        ret += byte4.to_bytes(1, "big")
        ret += (self.number & 0b11111111).to_bytes(1, "big")

        if self.count is not None:
            assert self.value is None
            ret += self.count.to_bytes(1, "big")
        elif self.value is not None:
            assert self.count is None
            ret += self.value.to_bytes(1, "big")
        return ret


class SwitchingAccessoriesCommand(AbstractLocIDCommand):
    position: int
    power: int
    value: int = None # time or special value. Time: t*10 ms


    def get_command(self) -> CommandSchema:
        return CommandSchema.SwitchingAccessories
    
    def get_other_data(self) -> bytes:
        ret = bytes()
        ret += position.to_bytes(1, "big")
        ret += power.to_bytes(1, "big")
        if value is not None:
            ret += value.to_bytes(2, "big")
        return ret
