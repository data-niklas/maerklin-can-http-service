from fastapi import APIRouter

from ...schemas.can_commands.system import *
from .helper import create_endpoint

router = APIRouter()


create_endpoint(router, "stop", SystemStopCommand)
create_endpoint(router, "halt", SystemHaltCommand)
create_endpoint(router, "go", SystemGoCommand)
create_endpoint(router, "locomotive_emergency_stop", LocomotiveEmergencyStopCommand)
create_endpoint(router, "locomotive_cycle_stop", LocomotiveCycleStopCommand)
create_endpoint(router, "locomotive_data_protocol", LocomotiveDataProtocolCommand)
create_endpoint(router, "accessory_decoder_switching_time", AccessoryDecoderSwitchingTimeCommand)
create_endpoint(router, "mfx_fast_read", MfxFastReadCommand)
create_endpoint(router, "enable_rail_protocol", EnableRailProtocolCommand)
create_endpoint(router, "set_mfx_register_counter", SetMfxRegisterCounterCommand)
create_endpoint(router, "overload", SystemOverloadCommand)
create_endpoint(router, "status", SystemStatusCommand)
create_endpoint(router, "set_system_identifier", SetSystemIdentifierCommand)
create_endpoint(router, "mfx_seek", MfxSeekCommand)
create_endpoint(router, "reset", SystemResetCommand)