from enum import Enum

from .base import AbstractCANMessage
from ..can import CommandSchema


class SystemSubcommandSchema(str, Enum):
    SystemStop = "SystemStop"
    SystemGo = "SystemGo"
    SystemHalt = "SystemHalt"
    LocomotiveEmergencyStop = "LocomotiveEmergencyStop"
    LocomotiveCycleStop =  "LocomotiveCycleStop"
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
    MM2_2040 = "MM2_2040",
    MM2_20 = "MM2_20",
    MM2_40 = "MM2_40",
    DCC_short_28 = "DCC_short_28",
    DCC_short_14 = "DCC_short_14",
    DCC_short_126 = "DCC_short_126",
    DCC_long_28 = "DCC_long_28",
    DCC_long_126 = "DCC_long_126"

class RailProtocol(Enum):
    MM2_2040 = 0x00,
    MM2_20 =  0x01,
    MM2_40 =  0x02,
    DCC_short_28 = 0x00,
    DCC_short_14 = 0x01,
    DCC_short_126 = 0x02,
    DCC_long_28 = 0x03,
    DCC_long_126 = 0x04 


class AbstractSystemCommand(AbstractCANMessage):
    id: int

    def get_command(self) -> CommandSchema:
        return CommandSchema.SystemCommand

    def get_other_data(self) -> bytes:
        raise NotImplentedError()
    
    def get_subcommand(self) -> SystemSubcommandSchema:
        raise NotImplentedError()

    def get_data(self) -> bytes:
        data = bytes()
        data += self.id.to_bytes(4, "big")
        subcommand = SystemSubcommand[self.get_subcommand().value]
        data += subcommand.value.to_bytes(1, "big")
        data += self.get_other_data()
        return data

class SystemStopCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemStop
    
    def get_other_data(self) -> bytes:
        return bytes()

class SystemGoCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemGo
    
    def get_other_data(self) -> bytes:
        return bytes()

class SystemHaltCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemHalt
    
    def get_other_data(self) -> bytes:
        return bytes()

class LocomotiveEmergencyStopCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.LocomotiveEmergencyStop
    
    def get_other_data(self) -> bytes:
        return bytes()

class LocomotiveCycleStopCommand(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.LocomotiveCycleStop
    
    def get_other_data(self) -> bytes:
        return bytes()
class LocomotiveDataProtocolCommand(AbstractSystemCommand):
    protocol: RailProtocolSchema

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.LocomotiveDataProtocol
    
    def get_other_data(self) -> bytes:
        return RailProtocol[self.protocol.value].value.to_bytes(1, "big")
class AccessoryDecoderSwitchingTimeCommand(AbstractSystemCommand):
    # time * 10ms
    time: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.AccessoryDecoderSwitchingTime
    
    def get_other_data(self) -> bytes:
        return self.time.to_bytes(2, "big")
class MfxFastReadCommand(AbstractSystemCommand):
    mfx_sid: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.MfxFastRead
    
    def get_other_data(self) -> bytes:
        return self.mfx_sid.to_bytes(2, "big")
class EnableRailProtocolCommand(AbstractSystemCommand):
    # only bits 0-2 are relevant. Bit enables or disables protocol
    # 0: MM2
    # 1: MFX
    # 2: DCC
    bitset: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.EnableRailProtocol
    
    def get_other_data(self) -> bytes:
        return self.bitset.to_bytes(1, "big")
class SetMfxRegisterCounterCommand(AbstractSystemCommand):
    counter: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SetMfxRegisterCounter
    
    def get_other_data(self) -> bytes:
        return self.counter.to_bytes(2, "big")

# Should always be a response
class SystemOverloadCommand(AbstractSystemCommand):
    # Who is responsible for overload
    channel: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemOverload
    
    def get_other_data(self) -> bytes:
        return self.channel.to_bytes(1, "big")
class SystemStatusCommand(AbstractSystemCommand):
    # Who is responsible for overload
    channel: int
    measured_value: int = None

    # TODO research DLC 8 konfiguration value request and DLC 7 TRUE / FALSE response

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemStatus
    
    def get_other_data(self) -> bytes:
        data = self.channel.to_bytes(1, "big")
        if self.measured_value is not None:
            data += self.measured_value.to_bytes(2, "big")
        return data
class SetSystemIdentifierCommand(AbstractSystemCommand):
    system_id: int = None


    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SetSystemIdentifier
    
    def get_other_data(self) -> bytes:
        if self.system_id is not None:
            return self.system_id.to_bytes(2, "big")
        return bytes()

# Mfx Seek is a lie...
# There is no Mfx Seek
class MfxSeekCommand(AbstractSystemCommand):

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.MfxSeek
    
    def get_other_data(self) -> bytes:
        return bytes()
class SystemResetCommand(AbstractSystemCommand):
    target: int

    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.SystemReset
    
    def get_other_data(self) -> bytes:
        return self.target.to_bytes(1, "big")