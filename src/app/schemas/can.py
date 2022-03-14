# TODO: throw useful errors when asserts don't match

from enum import Enum

from pydantic import BaseModel, Field

from ..utils.coding import bytes_to_str, int_to_bytes


class CommandSchema(str, Enum):
    SystemCommand = "SystemCommand"
    LocomotiveDiscovery = "LocomotiveDiscovery"
    MFXBind = "MFXBind"
    MFXVerify = "MFXVerify"
    LocomotiveSpeed = "LocomotiveSpeed"
    LocomotiveDirection = "LocomotiveDirection"
    LocomotiveFunction = "LocomotiveFunction"
    ReadConfig = "ReadConfig"
    WriteConfig = "WriteConfig"
    SwitchingAccessories = "SwitchingAccessories"
    AccessoriesConfig = "AccessoriesConfig"
    S88Polling = "S88Polling"
    S88Event = "S88Event"
    SX1Event = "SX1Event"
    ParticipantPing = "ParticipantPing"
    UpdateOffer = "UpdateOffer"
    ReadConfigData = "ReadConfigData"
    BootloaderCANBound = "BootloaderCANBound"
    BootloaderRailBound = "BootloaderRailBound"
    ServiceStatusDataConfiguration = "ServiceStatusDataConfiguration"
    RequestConfigData = "RequestConfigData"
    ConfigDataStream = "ConfigDataStream"
    DataStream60128 = "DataStream60128"
    UnknownCommand = "UnknownCommand"

class Command(Enum):
    SystemCommand = 0x00
    LocomotiveDiscovery = 0x01
    MFXBind = 0x02
    MFXVerify = 0x03
    LocomotiveSpeed = 0x04
    LocomotiveDirection = 0x05
    LocomotiveFunction = 0x06
    ReadConfig = 0x07
    WriteConfig = 0x08
    SwitchingAccessories = 0x0B
    AccessoriesConfig = 0x0C
    S88Polling = 0x10
    S88Event = 0x11
    SX1Event = 0x12
    ParticipantPing = 0x18
    UpdateOffer = 0x19
    ReadConfigData = 0x1A
    BootloaderCANBound = 0x1B
    BootloaderRailBound = 0x1C
    ServiceStatusDataConfiguration = 0x1D
    RequestConfigData = 0x20
    ConfigDataStream = 0x21
    DataStream60128 = 0x22
    UnknownCommand = -1

class MessageIdentifier(BaseModel):
    priority: int
    command: CommandSchema
    response: bool
    hash_value: int

    def to_bytes(self) -> bytes:
        ret = bytearray(2)

        assert self.priority < 5
        assert self.get_command().value < 256
        assert self.hash_value < (1 << 16)

        ret[0] = self.get_first_byte()
        ret[1] = self.get_second_byte()

        ret += int_to_bytes(self.hash_value, 2)

        return bytes(ret)
    
    def get_command(self) -> Command:
        return Command[self.command.value]
    
    def get_first_byte(self) -> int:
        ret = int(0)

        ret |= self.priority << 4
        ret |= self.get_command().value >> 7

        return ret
    
    def get_second_byte(self) -> int:
        ret = int(0)

        ret |= (self.get_command().value << 1) & 0b1111_1110
        ret |= (1 if self.response else 0)

        return ret
    
    def from_bytes(data: bytes):
        priority = data[0] >> 4
        command = (data[0] & 0b1) << 7
        command |= data[1] >> 1
        try:
            command = Command(command)
        except ValueError:
            command = Command.UnknownCommand
        command = CommandSchema[command.name]
        response = (data[1] & 0b1) > 0
        hash_value = int.from_bytes(data[2:], "big")

        return MessageIdentifier(priority=priority, command=command, response=response, hash_value=hash_value)

class CANMessage(BaseModel):
    message_id: MessageIdentifier
    data: str = Field("DE AD BE EF", description="String of hex values interpreted as bytes")

    def to_bytes(self) -> bytes:
        ret = bytearray()

        ret += self.message_id.to_bytes()
        
        data = self.get_data_bytes()
        
        length = len(data)
        assert length < 9
        ret += int_to_bytes(length, 1)
        
        if len(data) < 8:
            new_data = bytearray(8)
            new_data[:len(data)] = data
            data = bytes(new_data)
        ret += data

        return bytes(ret)
    
    def get_data_bytes(self) -> bytes:
        return bytes.fromhex(self.data)
    
    def from_bytes(data: bytes):
        message_id = MessageIdentifier.from_bytes(data[:4])
        length = data[4]
        data = data[5:5+length]
        data = bytes_to_str(data)

        return CANMessage(message_id=message_id, data=data)
