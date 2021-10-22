from fastapi import APIRouter

from ...schemas.can_commands.loc import *
from .helper import create_endpoint

router = APIRouter()

create_endpoint(router, "speed", LocomotiveSpeedCommand)
create_endpoint(router, "direction", LocomotiveDirectionCommand)
create_endpoint(router, "function", LocomotiveFunctionCommand)
create_endpoint(router, "read_config", ReadConfigCommand)
create_endpoint(router, "switch_accessory", SwitchingAccessoriesCommand)
create_endpoint(router, "s88_polling", S88PollingCommand)
create_endpoint(router, "write_config", WriteConfigCommand)
