from .base import AbstractCANMessage
from ..can import CommandSchema, CANMessage
from ...utils.coding import int_to_bytes, str_to_bytes, bytes_to_int, bytes_to_str
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

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.ParticipantPing:
            return None
        abstract_message = AbstractCANMessage.from_can_message(message)

        data = message.get_data_bytes()
        sender_id = None
        software_version = None
        device_id = None

        if len(data) > 0:
            sender_id = bytes_to_int(data[:4])

        if len(data) > 4:
            software_version = bytes_to_int(data[4:6])

        if len(data) > 6:
            device_id = bytes_to_int(data[6:8])

        return ParticipantPingCommand(sender_id=sender_id, software_version=software_version, device_id=device_id, **vars(abstract_message))

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

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.LocomotiveDiscovery:
            return None
        abstract_message = AbstractCANMessage.from_can_message(message)

        data = message.get_data_bytes()
        loc_id = None
        protocol = None
        mfx_range = None # 0 or 64
        ask_ratio = None

        if len(data) == 1:
            protocol_number = bytes_to_int(data[:1])
            if protocol_number > 0 and protocol_number <= 32:
                mfx_range = protocol_number
                protocol_number = 0
            elif protocol_number > 64 and protocol_number <= 96:
                mfx_range = protocol_number - 64
                protocol_number = 64
            protocol = ProtocolSchema(Protocol(protocol_number).name)

        if len(data) > 1:
            loc_id = bytes_to_int(data[:4])

            protocol_number = bytes_to_int(data[4:5])
            if protocol_number > 0 and protocol_number <= 32:
                mfx_range = protocol_number
                protocol_number = 0
            elif protocol_number > 64 and protocol_number <= 96:
                mfx_range = protocol_number - 64
                protocol_number = 64
            protocol = ProtocolSchema(Protocol(protocol_number).name)

        if len(data) > 5:
            ask_ratio = bytes_to_int(data[5:6])

        return LocomotiveDiscoveryCommand(loc_id=loc_id, protocol=protocol, mfx_range=mfx_range, ask_ratio=ask_ratio, **vars(abstract_message))


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
        
        if self.state_old is None and self.state_new is None and self.time is None:
            return ret

        assert not self.state_old is None
        assert not self.state_new is None
        assert not self.time is None
        ret += int_to_bytes(self.state_old, 1)
        ret += int_to_bytes(self.state_new, 1)
        ret += int_to_bytes(self.time, 2)

        return ret

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.S88Event:
            return None
        abstract_message = AbstractCANMessage.from_can_message(message)

        data = message.get_data_bytes()
        device_id = bytes_to_int(data[:2])
        contact_id = bytes_to_int(data[2:4])
        parameter = None 
        state_old = None 
        state_new = None 
        time = None 

        if len(data) == 5:
            parameter = bytes_to_int(data[4:5])
        elif len(data) > 5:
            state_old = bytes_to_int(data[4:5])
            state_new = bytes_to_int(data[5:6])
            time = bytes_to_int(data[6:8])


        return S88EventCommand(data=data, device_id=device_id, contact_id=contact_id, parameter=parameter, state_old=state_old, state_new=state_new,time=time, **vars(abstract_message))



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
        if message.message_id.command != CommandSchema.RequestConfigData:
            return None
        abstract_message = AbstractCANMessage.from_can_message(message)
        
        
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

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.ServiceStatusDataConfiguration:
            return None
        abstract_message = AbstractCANMessage.from_can_message(message)

        raw_data = message.get_data_bytes()

        device_id = None
        index = None
        count = None
        data = None

        if len(raw_data) > 0 and len(raw_data) < 8:
            device_id = bytes_to_int(raw_data[:4])
            index = bytes_to_int(raw_data[4:5])
            if len(raw_data) == 6:
                count = bytes_to_int(raw_data[5:6])
        elif len(raw_data) == 8:
            data = bytes_to_str(raw_data)


        return ServiceStatusDataConfigurationCommand(device_id=device_id, index=index, count=count, data=data, **vars(abstract_message))


class ConfigDataStreamCommand(AbstractCANMessage):
    file_length: int = None
    crc: int = None
    byte6: int = None
    data: str = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.ConfigDataStream
    
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

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.ConfigDataStream:
            return None
        abstract_message = AbstractCANMessage.from_can_message(message)

        raw_data = message.get_data_bytes()

        file_length = None
        crc = None
        byte6 = None
        data = None

        if len(raw_data) > 0 and len(raw_data) < 8:
            file_length = bytes_to_int(raw_data[:4])
            crc = bytes_to_int(raw_data[4:6])
            if len(raw_data) == 7:
                byte6 = bytes_to_int(raw_data[6:7])
        elif len(raw_data) == 8:
            data = bytes_to_str(raw_data)


        return ConfigDataStreamCommand(file_length=file_length, crc=crc, byte6=byte6, data=data, **vars(abstract_message))


class BootloaderCANBoundCommand(AbstractCANMessage):
    data: str = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.BootloaderCANBound
    
    def get_data(self) -> bytes:
        if self.data is None:
            return bytes()
        return bytes.fromhex(self.data)

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.BootloaderCANBound:
            return None
        abstract_message = AbstractCANMessage.from_can_message(message)

        data = message.get_data_bytes()
        if len(data) == 0:
            data = None
        else:
            data = bytes_to_str(data)


        return BootloaderCANBoundCommand(data=data, **vars(abstract_message))
