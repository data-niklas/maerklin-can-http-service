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

class LocomotiveEmergencyStop(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.LocomotiveEmergencyStop
    
    def get_other_data(self) -> bytes:
        return bytes()

class LocomotiveCycleStop(AbstractSystemCommand):
    def get_subcommand(self) -> SystemSubcommandSchema:
        return SystemSubcommandSchema.LocomotiveCycleStop
    
    def get_other_data(self) -> bytes:
        return bytes()