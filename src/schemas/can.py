# TODO: throw useful errors when asserts don't match

from enum import Enum

from pydantic import BaseModel


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
    ServiceStatusDataConfiguration = "ServiceStatusDataConfiguration"
    RequestConfigData = "RequestConfigData"
    Stream = "Stream"
    DataStream60128 = "DataStream60128"

class Command(Enum):
    SystemCommand = 0x00
    LocomotiveDiscovery = 0x02
    MFXBind = 0x04
    MFXVerify = 0x06
    LocomotiveSpeed = 0x08
    LocomotiveDirection = 0x0A
    LocomotiveFunction = 0x0C
    ReadConfig = 0x0E
    WriteConfig = 0x10
    SwitchingAccessories = 0x16
    AccessoriesConfig = 0x18
    S88Polling = 0x20
    S88Event = 0x22
    SX1Event = 0x24
    ParticipantPing = 0x30
    UpdateOffer = 0x32
    ReadConfigData = 0x34
    BootloaderCANBound = 0x36
    ServiceStatusDataConfiguration = 0x38
    RequestConfigData = 0x40
    Stream = 0x42
    DataStream60128 = 0x44

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

        ret += self.hash_value.to_bytes(2, "big")

        return bytes(ret)
    
    def get_command(self) -> Command:
        return Command[self.command.value]
    
    def get_first_byte(self) -> int:
        ret = int(0)

        ret |= self.priority << 4
        ret |= self.get_command().value >> 4

        return ret
    
    def get_second_byte(self) -> int:
        ret = int(0)

        ret |= (self.get_command().value << 4) & 0b11110000
        ret |= (1 if self.response else 0) << 3 # padded with zeros here before hash
        # TODO: test if works

        return ret
    
    def from_bytes(data: bytes):
        priority = data[0] >> 4
        command = (data[0] & 0b1111) << 4
        command |= data[1] >> 4
        command = Command(command)
        command = CommandSchema[command.name]
        response = (data[1] & 0b1000) > 0
        hash_value = int.from_bytes(data[2:], "big")

        return MessageIdentifier(priority=priority, command=command, response=response, hash_value=hash_value)

class CANMessage(BaseModel):
    message_id: MessageIdentifier
    length: int
    data: bytes

    def to_bytes(self) -> bytes:
        ret = bytearray()

        ret += self.message_id.to_bytes()
        assert self.length < 16
        ret += self.length.to_bytes(1, "big")
        data = self.data
        assert self.length == len(data)
        assert len(data) < 9
        if len(data) < 8:
            new_data = bytearray(8)
            new_data[:len(data)] = data
            data = bytes(new_data)
        ret += data

        return bytes(ret)
    
    def from_bytes(data: bytes):
        message_id = MessageIdentifier.from_bytes(data[:4])
        length = data[4]
        data = data[5:]

        return CANMessage(message_id=message_id, length=length, data=data)