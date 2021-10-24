from typing import Type

from ...schemas.can import CANMessage
from ...schemas.can_commands.base import AbstractCANMessage
from ...schemas.can_commands import *


registered_types: list[Type[AbstractCANMessage]] = list()

def convert_to_abstract(message: CANMessage) -> AbstractCANMessage:
    for t in registered_types:
        abstract_message = t.from_can_message(message)
        if abstract_message is not None:
            return abstract_message
    return None

# general.py
registered_types.extends([
    ParticipantPingCommand,
    LocomotiveDiscoveryCommand,
    S88EventCommand,
    RequestConfigDataCommand,
    ServiceStatusDataConfigurationCommand,
    ConfigDataStreamCommand
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