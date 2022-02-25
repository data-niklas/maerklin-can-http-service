from enum import Enum

from .base import AbstractCANMessage
from ..can import CommandSchema, CANMessage
from ...utils.coding import int_to_bytes, bytes_to_int


class SystemSubcommandSchema(str, Enum):
    SystemStop = "SystemStop"
    SystemGo = "SystemGo"
    SystemHalt = "SystemHalt"
    LocomotiveEmergencyStop = "LocomotiveEmergencyStop"
    LocomotiveCycleStop = "LocomotiveCycleStop"
    LocomotiveDataProtocol = "LocomotiveDataProtocol"
    AccessoryDecoderSwitchingTime = "AccessoryDecoderSwitchingTime"
    MfxFastRead = "MfxFastRead"
    EnableRailProtocol = "EnableRailProtocol"
    SetMfxRegisterCounter = "SetMfxRegisterCounter"
    SystemOverload = "SystemOverload"
    SystemStatus = "SystemStatus"
    SetSystemIdentifier = "SetSystemIdentifier"
    MfxSeek = "MfxSeek"
    SystemReset = "SystemReset"


class SystemSubcommand(Enum):
    SystemStop = 0x00
    SystemGo = 0x01
    SystemHalt = 0x02
    LocomotiveEmergencyStop = 0x03
    LocomotiveCycleStop = 0x04
    LocomotiveDataProtocol = 0x05
    AccessoryDecoderSwitchingTime = 0x06
    MfxFastRead = 0x07
    EnableRailProtocol = 0x08
    SetMfxRegisterCounter = 0x09
    SystemOverload = 0x0A
    SystemStatus = 0x0B
    SetSystemIdentifier = 0x0C
    MfxSeek = 0x30
    SystemReset = 0x80


class RailProtocolSchema(str, Enum):
    MM2_2040 = "MM2_2040"
    MM2_20 = "MM2_20"
    MM2_40 = "MM2_40"
    DCC_short_28 = "DCC_short_28"
    DCC_short_14 = "DCC_short_14"
    DCC_short_126 = "DCC_short_126"
    DCC_long_28 = "DCC_long_28"
    DCC_long_126 = "DCC_long_126"


class RailProtocol(Enum):
    MM2_2040 = 0x00
    MM2_20 = 0x01
    MM2_40 = 0x02
    DCC_short_28 = 0x00
    DCC_short_14 = 0x01
    DCC_short_126 = 0x02
    DCC_long_28 = 0x03
    DCC_long_126 = 0x04


class AbstractSystemCommand(AbstractCANMessage):
    id: int

    def get_command(self) -> CommandSchema:
        return CommandSchema.SystemCommand

    def get_other_data(self) -> bytes:
        raise NotImplementedError()

    def get_subcommand(self) -> SystemSubcommandSchema:
        raise NotImplementedError()

    def get_data(self) -> bytes:
        data = bytes()
        data += int_to_bytes(self.id, 4)
        subcommand = SystemSubcommand[self.get_subcommand().value]
        data += int_to_bytes(subcommand.value, 1)
        data += self.get_other_data()
        return data

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        abstract_message = AbstractCANMessage.from_can_message(message)

        data = message.get_data_bytes()
        assert len(data) >= 5

        id = bytes_to_int(data[:4])
        return AbstractSystemCommand(id=id, **vars(abstract_message))

    def get_subcommand_from_data(data: bytes) -> SystemSubcommandSchema:
        subcommand_number = bytes_to_int(data[4:5])
        return SystemSubcommandSchema(SystemSubcommand(subcommand_number).name)


class SystemStopCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemStop

    def get_other_data(self) -> bytes:
        return bytes()

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.SystemStop:
            return None

        return SystemStopCommand(**vars(abstract_message))


class SystemGoCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemGo

    def get_other_data(self) -> bytes:
        return bytes()

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.SystemGo:
            return None

        return SystemGoCommand(**vars(abstract_message))


class SystemHaltCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemHalt

    def get_other_data(self) -> bytes:
        return bytes()

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.SystemHalt:
            return None

        return SystemHaltCommand(**vars(abstract_message))


class LocomotiveEmergencyStopCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.LocomotiveEmergencyStop

    def get_other_data(self) -> bytes:
        return bytes()

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.LocomotiveEmergencyStop:
            return None

        return LocomotiveEmergencyStopCommand(**vars(abstract_message))


class LocomotiveCycleStopCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.LocomotiveCycleStop

    def get_other_data(self) -> bytes:
        return bytes()

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.LocomotiveCycleStop:
            return None

        return LocomotiveCycleStopCommand(**vars(abstract_message))


class LocomotiveDataProtocolCommand(AbstractSystemCommand):
    protocol: RailProtocolSchema

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.LocomotiveDataProtocol

    def get_other_data(self) -> bytes:
        return int_to_bytes(RailProtocol[self.protocol.value].value, 1)

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.LocomotiveDataProtocol:
            return None

        protocol_number = bytes_to_int(data[5:6])
        protocol = RailProtocolSchema(RailProtocol(protocol_number).name)
        return LocomotiveDataProtocolCommand(protocol=protocol, **vars(abstract_message))


class AccessoryDecoderSwitchingTimeCommand(AbstractSystemCommand):
    # time * 10ms
    time: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.AccessoryDecoderSwitchingTime

    def get_other_data(self) -> bytes:
        return int_to_bytes(self.time, 2)

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.AccessoryDecoderSwitchingTime:
            return None

        time = bytes_to_int(data[5:7])
        return AccessoryDecoderSwitchingTimeCommand(time=time, **vars(abstract_message))


class MfxFastReadCommand(AbstractSystemCommand):
    mfx_sid: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.MfxFastRead

    def get_other_data(self) -> bytes:
        return int_to_bytes(self.mfx_sid, 2)

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.MfxFastRead:
            return None

        mfx_sid = bytes_to_int(data[5:7])
        return MfxFastReadCommand(mfx_sid=mfx_sid, **vars(abstract_message))


class EnableRailProtocolCommand(AbstractSystemCommand):
    # only bits 0-2 are relevant. Bit enables or disables protocol
    # 0: MM2
    # 1: MFX
    # 2: DCC
    bitset: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.EnableRailProtocol

    def get_other_data(self) -> bytes:
        return int_to_bytes(self.bitset, 1)

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.EnableRailProtocol:
            return None

        bitset = bytes_to_int(data[5:6])
        return EnableRailProtocolCommand(bitset=bitset, **vars(abstract_message))


class SetMfxRegisterCounterCommand(AbstractSystemCommand):
    counter: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SetMfxRegisterCounter

    def get_other_data(self) -> bytes:
        return int_to_bytes(self.counter, 2)

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.SetMfxRegisterCounter:
            return None

        counter = bytes_to_int(data[5:7])
        return SetMfxRegisterCounterCommand(counter=counter, **vars(abstract_message))

# Should always be a response


class SystemOverloadCommand(AbstractSystemCommand):
    # Who is responsible for overload
    channel: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemOverload

    def get_other_data(self) -> bytes:
        return int_to_bytes(self.channel, 1)

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.SystemOverload:
            return None

        channel = bytes_to_int(data[5:6])
        return SystemOverloadCommand(channel=channel, **vars(abstract_message))


class SystemStatusCommand(AbstractSystemCommand):
    # Who is responsible for overload
    channel: int
    measured_value: int = None

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemStatus

    def get_other_data(self) -> bytes:
        data = int_to_bytes(self.channel, 1)
        if self.measured_value is not None:
            data += int_to_bytes(self.measured_value, 2)
        return data

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.SystemStatus:
            return None

        channel = bytes_to_int(data[5:6])
        measured_value = None
        if len(data) == 8:
            measured_value = bytes_to_int(data[6:8])
        if len(data) == 7:
            measured_value = bool(data[6])
        return SystemStatusCommand(channel=channel, measured_value=measured_value, **vars(abstract_message))


class SetSystemIdentifierCommand(AbstractSystemCommand):
    system_id: int = None

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SetSystemIdentifier

    def get_other_data(self) -> bytes:
        if self.system_id is not None:
            return int_to_bytes(self.system_id, 2)
        return bytes()

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.SetSystemIdentifier:
            return None

        system_id = None
        if len(data) > 5:
            system_id = bytes_to_int(data[5:7])
        return SetSystemIdentifierCommand(system_id=system_id, **vars(abstract_message))

# Mfx Seek is a lie...
# There is no Mfx Seek


class MfxSeekCommand(AbstractSystemCommand):

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.MfxSeek

    def get_other_data(self) -> bytes:
        return bytes()

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.MfxSeek:
            return None

        return MfxSeekCommand(**vars(abstract_message))


class SystemResetCommand(AbstractSystemCommand):
    target: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemReset

    def get_other_data(self) -> bytes:
        return int_to_bytes(self.target, 1)

    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        command = message.message_id.command
        if command != CommandSchema.SystemCommand:
            return None
        abstract_message = AbstractSystemCommand.from_can_message(message)
        data = message.get_data_bytes()
        subcommand = AbstractSystemCommand.get_subcommand_from_data(data)
        if subcommand != SystemSubcommandSchema.SystemReset:
            return None

        target = bytes_to_int(data[5:6])
        return SystemResetCommand(target=target, **vars(abstract_message))
