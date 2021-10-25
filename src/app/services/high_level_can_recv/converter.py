from typing import Type

from ...schemas.can import CANMessage
from ...schemas.can_commands.base import AbstractCANMessage
from ...schemas.can_commands import *


# registered_types: list[Type[AbstractCANMessage]] = list()
registered_types = list()

def convert_to_abstract(message: CANMessage) -> AbstractCANMessage:
    for t in registered_types:
        abstract_message = t.from_can_message(message)
        if abstract_message is not None:
            return abstract_message
    return None

# general.py
registered_types.extend([
    ParticipantPingCommand,
    LocomotiveDiscoveryCommand,
    S88EventCommand,
    RequestConfigDataCommand,
    ServiceStatusDataConfigurationCommand,
    ConfigDataStreamCommand,
    BootloaderCANBoundCommand
])

# loc.py
registered_types.extend([
    LocomotiveSpeedCommand,
    LocomotiveDirectionCommand,
    LocomotiveFunctionCommand,
    ReadConfigCommand,
    WriteConfigCommand,
    SwitchingAccessoriesCommand,
    S88PollingCommand
])

# mfx.py
registered_types.extend([
    MfxBindCommand,
    MfxVerifyCommand
])

# system.py
registered_types.extend([
    SystemStopCommand,
    SystemGoCommand,
    SystemHaltCommand,
    LocomotiveEmergencyStopCommand,
    LocomotiveCycleStopCommand,
    LocomotiveDataProtocolCommand,
    AccessoryDecoderSwitchingTimeCommand,
    MfxFastReadCommand,
    EnableRailProtocolCommand,
    SetMfxRegisterCounterCommand,
    SystemOverloadCommand,
    SystemStatusCommand,
    SetSystemIdentifierCommand,
    MfxSeekCommand,
    SystemResetCommand
])

type_map = dict()
# general.py
type_map[ParticipantPingCommand.__name__] = ParticipantPingCommand
type_map[LocomotiveDiscoveryCommand.__name__] = LocomotiveDiscoveryCommand
type_map[S88EventCommand.__name__] = S88EventCommand
type_map[RequestConfigDataCommand.__name__] = RequestConfigDataCommand
type_map[ServiceStatusDataConfigurationCommand.__name__] = ServiceStatusDataConfigurationCommand
type_map[ConfigDataStreamCommand.__name__] = ConfigDataStreamCommand
type_map[BootloaderCANBoundCommand.__name__] = BootloaderCANBoundCommand


# loc.py
type_map[LocomotiveSpeedCommand.__name__] = LocomotiveSpeedCommand
type_map[LocomotiveDirectionCommand.__name__] = LocomotiveDirectionCommand
type_map[LocomotiveFunctionCommand.__name__] = LocomotiveFunctionCommand
type_map[ReadConfigCommand.__name__] = ReadConfigCommand
type_map[WriteConfigCommand.__name__] = WriteConfigCommand
type_map[SwitchingAccessoriesCommand.__name__] = SwitchingAccessoriesCommand
type_map[S88PollingCommand.__name__] = S88PollingCommand

# mfx.py
type_map[MfxBindCommand.__name__] = MfxBindCommand
type_map[MfxVerifyCommand.__name__] = MfxVerifyCommand

# system.py
type_map[SystemStopCommand.__name__] = SystemStopCommand
type_map[SystemGoCommand.__name__] = SystemGoCommand
type_map[SystemHaltCommand.__name__] = SystemHaltCommand
type_map[LocomotiveEmergencyStopCommand.__name__] = LocomotiveEmergencyStopCommand
type_map[LocomotiveCycleStopCommand.__name__] = LocomotiveCycleStopCommand
type_map[LocomotiveDataProtocolCommand.__name__] = LocomotiveDataProtocolCommand
type_map[AccessoryDecoderSwitchingTimeCommand.__name__] = AccessoryDecoderSwitchingTimeCommand
type_map[MfxFastReadCommand.__name__] = MfxFastReadCommand
type_map[EnableRailProtocolCommand.__name__] = EnableRailProtocolCommand
type_map[SetMfxRegisterCounterCommand.__name__] = SetMfxRegisterCounterCommand
type_map[SystemOverloadCommand.__name__] = SystemOverloadCommand
type_map[SystemStatusCommand.__name__] = SystemStatusCommand
type_map[SetSystemIdentifierCommand.__name__] = SetSystemIdentifierCommand
type_map[MfxSeekCommand.__name__] = MfxSeekCommand
type_map[SystemResetCommand.__name__] = SystemResetCommand