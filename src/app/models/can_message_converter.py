from app.models.can_message import *
from ..schemas.can_commands import AbstractCANMessage as PydanticAbstractCANMessage
registered_models = list()


def convert_to_model(message: PydanticAbstractCANMessage) -> AbstractCANMessage:
    for model in registered_models:
        abstract_message = model.from_schema(message)
        if abstract_message is not None:
            return abstract_message
    return None


registered_models.extend([
    LocomotiveSpeedMessage,
    LocomotiveDirectionMessage,
    LocomotiveFunctionMessage,
    ReadConfigMessage,
    WriteConfigMessage,
    RequestConfigDataMessage
])

registered_models.extend([
    SwitchingAccessoriesMessage,
    S88PollingMessage,
    S88EventMessage,
    ConfigMessage,
    ConfigUsageMessage,
    ConfigLocomotiveMessage,
    ParticipantPingMessage,
    LocomotiveDiscoveryMessage,
    ServiceStatusDataConfigurationMessage,
    BootloaderCANBoundMessage
])

registered_models.extend([
    SystemStateMessage,
    LocomotiveEmergencyStopMessage,
    LocomotiveCycleStopMessage,
    LocomotiveDataProtocolMessage,
    AccessoryDecoderSwitchingTimeMessage,
    MfxFastReadMessage,
    EnableRailProtocolCommand,
    SetMfxRegisterCounterMessage,
    SystemOverloadMessage,
    SystemStatusMessage,
    SetSystemIdentifierMessage,
    MfxSeekMessage,
    SystemResetMessage
])


registered_models.extend([
    MfxBindMessage,
    MfxVerifyMessage
])

registered_models.extend([
    LocomotiveMetricMessage
])