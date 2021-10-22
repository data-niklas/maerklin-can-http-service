from .base import AbstractCANMessage
from ..can import CommandSchema, CANMessage
from ...utils.coding import int_to_bytes, str_to_bytes
from enum import Enum

class ParticipantPingCommand(AbstractCANMessage):
    sender_id: int = None
    software_version: int = None
    device_id: int = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.ParticipantPing
    
    def get_data(self) -> bytes:
        if self.sender_id is None:
            assert self.software_version is None
            assert self.device_id is None
            return bytes()
        ret = bytes()
        assert self.sender_id is not None
        assert self.software_version is not None
        assert self.device_id is not None

        ret += int_to_bytes(self.sender_id, 4)
        ret += int_to_bytes(self.software_version, 2)
        ret += int_to_bytes(self.device_id, 2)

        return ret

class ProtocolSchema(str, Enum):
    MFX = "MFX"
    MM2_20 =  "MM2_20"
    MM2_40 =  "MM2_40"
    DCC_read_short = "DCC_read_short"
    DCC_read_long = "DCC_read_long"
    DCC_identify = "DCC_identify"
    SX1_read = "SX1_read"
    SX1_identify = "SX1_identify"
    MFX_main = "MFX_main" 

class Protocol(Enum):
    MFX =  0
    MM2_20 =  33
    MM2_40 =  34
    DCC_read_short = 35
    DCC_read_long = 36
    DCC_identify = 37
    SX1_read = 38
    SX1_identify = 39
    MFX_main = 64 

class LocomotiveDiscoveryCommand(AbstractCANMessage):
    loc_id: int = None
    protocol: ProtocolSchema = None
    mfx_range: int = None
    ask_ratio: int = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.LocomotiveDiscovery
    
    def get_data(self) -> bytes:
        ret = bytes()

        if self.protocol is None:
            assert self.loc_id is None
            assert self.mfx_range is None
            assert self.ask_ratio is None
            return ret

        if not self.loc_id is None:
            ret += int_to_bytes(self.loc_id, 4)

        protocol = Protocol[self.protocol.value].value

        if not self.mfx_range is None:
            assert not self.protocol is None
            assert self.protocol in [ProtocolSchema.MFX, ProtocolSchema.MFX_main]
            ret += int_to_bytes(self.mfx_range + protocol, 1)
        else:
            print(protocol)
            ret += int_to_bytes(protocol, 1)

        if not self.ask_ratio is None:
            ret += int_to_bytes(self.ask_ratio, 1)
            assert not self.loc_id is None

        return ret

class S88EventCommand(AbstractCANMessage):
    device_id: int
    contact_id: int
    parameter: int = None 
    state_old: int = None 
    state_new: int = None 
    time: int = None 


    def get_command(self) -> CommandSchema:
        return CommandSchema.S88Event
    
    def get_data(self) -> bytes:
        ret = bytes()
        ret += int_to_bytes(self.device_id, 2)
        ret += int_to_bytes(self.contact_id, 2)
        
        if not self.parameter is None:
            assert self.state_old is None
            assert self.state_new is None
            assert self.time is None
            ret += int_to_bytes(self.parameter, 1)
            return ret
        

        assert not self.state_old is None
        assert not self.state_new is None
        assert not self.time is None
        ret += int_to_bytes(self.state_old, 1)
        ret += int_to_bytes(self.state_new, 1)
        ret += int_to_bytes(self.time, 2)

        return ret


class RequestConfigDataCommand(AbstractCANMessage):
    filename: str

    def get_command(self) -> CommandSchema:
        return CommandSchema.RequestConfigData
    
    def get_data(self) -> bytes:
        ret = bytes()
        ret += str_to_bytes(self.filename)
        ret_len = len(ret)
        assert ret_len <= 8

        ret += bytes(8 - ret_len)# Padding

        return ret
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        abstract_message = AbstractCANMessage.from_can_message(message)
        
        if message.message_id.command != CommandSchema.RequestConfigData:
            return None

        data = message.get_data_bytes()
        assert len(data) == 8
        filename = bytes(filter(lambda b: b != 0, data)).decode("utf-8") # remove padding and decode

        return RequestConfigDataCommand(filename=filename, **vars(abstract_message))

class ServiceStatusDataConfigurationCommand(AbstractCANMessage):
    device_id: int = None
    index: int = None
    count: int = None
    data: str = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.ServiceStatusDataConfiguration
    
    def get_data(self) -> bytes:
        ret = bytes()
        
        if not self.data is None:
            assert self.device_id is None
            assert self.index is None
            assert self.count is None
            assert self.response
            ret = bytes.fromhex(self.data)
            assert len(ret) == 8
            return ret

        assert self.device_id is not None
        assert self.index is not None
        
        ret += int_to_bytes(self.device_id, 4)
        ret += int_to_bytes(self.index, 1)
        
        if self.count is not None:
            assert self.response
            ret += int_to_bytes(self.count, 1)
        else:
            assert not self.response

        return ret

class ConfigDataStreamCommand(AbstractCANMessage):
    file_length: int = None
    crc: int = None
    byte6: int = None
    data: str = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.RequestConfigData
    
    def get_data(self) -> bytes:
        ret = bytes()
        if not self.data is None:
            assert self.byte6 is None
            assert self.file_length is None
            assert self.crc is None
            ret += bytes.fromhex(self.data)
            return ret

        assert not self.file_length is None
        assert not self.crc is None
        ret += int_to_bytes(self.file_length, 4)
        ret += int_to_bytes(self.crc, 2)

        if not self.byte6 is None:
            ret += int_to_bytes(self.byte6, 1)

        return ret
