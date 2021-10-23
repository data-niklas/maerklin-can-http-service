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

registered_types.append(RequestConfigDataCommand)
registered_types.append(LocomotiveSpeedCommand)
registered_types.append(LocomotiveDirectionCommand)
registered_types.append(MfxBindCommand)
registered_types.append(MfxVerifyCommand)