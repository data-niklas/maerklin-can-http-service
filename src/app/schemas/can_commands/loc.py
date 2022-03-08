from enum import Enum

from pydantic import BaseModel

from .base import AbstractCANMessage
from ..can import CommandSchema, CANMessage
from ...utils.coding import int_to_bytes, bytes_to_int

class AbstractLocIDCommand(AbstractCANMessage):
    loc_id: int

    def get_other_data(self) -> bytes:
        raise NotImplementedError()

    def get_data(self) -> bytes:
        data = bytes()
        data += int_to_bytes(self.loc_id, 4)
        data += self.get_other_data()
        return data
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        abstract_message = AbstractCANMessage.from_can_message(message)

        data = message.get_data_bytes()
        assert len(data) >= 4

        loc_id = bytes_to_int(data[:4])

        return AbstractLocIDCommand(loc_id=loc_id, **vars(abstract_message))

class LocomotiveSpeedCommand(AbstractLocIDCommand):
    speed: int = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.LocomotiveSpeed
    
    def get_other_data(self) -> bytes:
        if self.speed is None:
            return bytes()
        assert self.speed <= 1000
        return int_to_bytes(self.speed, 2)
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.LocomotiveSpeed:
            return None

        abstract_message = AbstractLocIDCommand.from_can_message(message)
        data = message.get_data_bytes()
        speed = None
        if len(data) > 4:
            speed = bytes_to_int(data[4:6])

        return LocomotiveSpeedCommand(speed=speed, **vars(abstract_message))

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
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.LocomotiveDirection:
            return None
        abstract_message = AbstractLocIDCommand.from_can_message(message)

        data = message.get_data_bytes()
        direction = None
        assert len(data) < 6
        if len(data) > 4:
            direction = bytes_to_int(data[4:5])
            if direction == 1:
                direction = LocomotiveDirection.Forwards
            elif direction == 2:
                direction = LocomotiveDirection.Backwards
            elif direction == 3:
                direction = LocomotiveDirection.Toggle
            else:
                direction = LocomotiveDirection.Keep

        return LocomotiveDirectionCommand(direction=direction, **vars(abstract_message))

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
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.LocomotiveFunction:
            return None
        abstract_message = AbstractLocIDCommand.from_can_message(message)

        data = message.get_data_bytes()
        function = bytes_to_int(data[4:5])
        
        value = None
        if len(data) > 5:
            value = bytes_to_int(data[5:6])
        
        function_value = None
        if len(data) > 6:
            assert len(data) == 8
            function_value = bytes_to_int(data[6:8])

        return LocomotiveFunctionCommand(function=function, value=value, function_value=function_value, **vars(abstract_message))

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
            assert not self.response
            ret += int_to_bytes(self.count, 1)
        elif self.value is not None:
            assert self.count is None
            assert self.response
            ret += int_to_bytes(self.value, 1)
        return ret
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.ReadConfig:
            return None
        abstract_message = AbstractLocIDCommand.from_can_message(message)

        data = message.get_data_bytes()
        
        assert len(data) == 6 or len(data) == 7

        byte4 = bytes_to_int(data[4:5])
        byte5 = bytes_to_int(data[5:6])

        index = byte4 >> 2
        number = (byte4 & 0b0000_0011) << 8
        number |= byte5

        count = None
        value = None
        if len(data) == 7:
            byte6 = bytes_to_int(data[6:7])
            if message.message_id.response:
                value = byte6
            else:
                count = byte6

        return ReadConfigCommand(index=index, number=number, count=count, value=value, **vars(abstract_message))

class DCCProgramming(str, Enum):
    DirectProgramming = "DirectProgramming"
    RegisterProgramming = "RegisterProgramming"
    BitProgramming = "BitProgramming"

class WriteConfigControlByte(BaseModel):
    is_main: bool
    is_multi_byte: bool
    dcc_programming: DCCProgramming

    def get_value(self):
        ret = 0

        if self.is_main:
            ret |= 0b1000_0000
        if self.is_multi_byte:
            ret |= 0b0100_0000
        
        if self.dcc_programming == DCCProgramming.DirectProgramming:
            ret |= 0b0000_0000
        elif self.dcc_programming == DCCProgramming.RegisterProgramming:
            ret |= 0b0001_0000
        elif self.dcc_programming == DCCProgramming.BitProgramming:
            ret |= 0b0010_0000
        else:
            raise NotImplementedError()

        return ret
    
    def from_value(value: int):
        is_main = (value & 0b1000_0000) > 0
        is_multi_byte = (value & 0b0100_0000) > 0
        dcc_programming = DCCProgramming.DirectProgramming
        if (value & 0b0001_0000) > 0:
            dcc_programming = DCCProgramming.RegisterProgramming
        if (value & 0b0010_0000) > 0:
            dcc_programming = DCCProgramming.BitProgramming
        assert bin(value).count("1") < 4 # either Register or BitProgramming

        return WriteConfigControlByte(is_main=is_main, is_multi_byte=is_multi_byte, dcc_programming=dcc_programming)

class WriteConfigResultByte(BaseModel):
    is_write_successful: bool
    is_verify_successful: bool

    def get_value(self):
        ret = 0

        if self.is_write_successful:
            ret |= 1 << 7
        if self.is_verify_successful:
            ret |= 1 << 6

        return ret
    
    def from_value(value):
        is_write_successful = (value & 0b1000_0000) > 0
        is_verify_successful = (value & 0b0100_0000) > 0

        return WriteConfigResultByte(is_write_successful=is_write_successful, is_verify_successful=is_verify_successful)

class WriteConfigCommand(AbstractLocIDCommand):
    index: int # 6 bit
    number: int # 10 bit
    value: int
    control: WriteConfigControlByte = None
    result: WriteConfigResultByte = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.WriteConfig
    
    def get_other_data(self) -> bytes:
        ret = bytes()

        byte4 = self.index << 2
        byte4 |= (self.number >> 8) & 0b0000_0011
        ret += int_to_bytes(byte4, 1)
        ret += int_to_bytes(self.number & 0b1111_1111, 1)

        
        ret += int_to_bytes(self.value, 1)
        
        assert (self.control is None) ^ (self.result is None) # exactly one of them is set

        if self.control is not None:
            assert not self.response
            ret += int_to_bytes(self.control.get_value(), 1)
        if self.result is not None:
            assert self.response
            ret += int_to_bytes(self.result.get_value(), 1)

        return ret
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.WriteConfig:
            return None
        abstract_message = AbstractLocIDCommand.from_can_message(message)

        data = message.get_data_bytes()
        
        assert len(data) == 8

        byte4 = bytes_to_int(data[4:5])
        byte5 = bytes_to_int(data[5:6])

        index = byte4 >> 2
        number = (byte4 & 0b0000_0011) << 8
        number |= byte5

        value = bytes_to_int(data[6:7])

        control = None
        result = None
        byte7 = bytes_to_int(data[7:8])
        if message.message_id.response:
            result = WriteConfigResultByte.from_value(byte7)
        else:
            control = WriteConfigControlByte.from_value(byte7)

        return WriteConfigCommand(index=index, number=number, value=value, control=control, result=result, **vars(abstract_message))


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

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SwitchingAccessories:
            return None
        abstract_message = AbstractLocIDCommand.from_can_message(message)

        data = message.get_data_bytes()
        assert len(data) in [6,8]

        position = bytes_to_int(data[4:5])
        power = bytes_to_int(data[5:6])

        value = None
        if len(data) == 8:
            value = bytes_to_int(data[6:8])

        return SwitchingAccessoriesCommand(position=position, power=power, value=value, **vars(abstract_message))


class S88PollingCommand(AbstractLocIDCommand):
    module_count: int = None
    module: int = None
    state: int = None 


    def get_command(self) -> CommandSchema:
        return CommandSchema.S88Polling
    
    def get_other_data(self) -> bytes:
        ret = bytes()
        if not self.module_count is None:
            ret += int_to_bytes(self.module_count, 1)
            assert not self.response
            assert self.module is None
            assert self.state is None
            return ret

        assert not self.module is None
        assert not self.state is None
        assert self.response
        ret += int_to_bytes(self.module, 1)
        ret += int_to_bytes(self.state, 2)
        return ret

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.S88Polling:
            return None
        abstract_message = AbstractLocIDCommand.from_can_message(message)

        data = message.get_data_bytes()
        assert len(data) in [5,7]

        module_count = None
        module = None
        state = None 

        if len(data) == 5:
            module_count = bytes_to_int(data[4:5])
        else: # data has len 7
            module = bytes_to_int(data[4:5])
            state = bytes_to_int(data[5:7])

        return S88PollingCommand(module_count=module_count, module=module, state=state, **vars(abstract_message))
