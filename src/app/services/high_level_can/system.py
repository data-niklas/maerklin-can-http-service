from fastapi import APIRouter, Header
from typing import Type

from ...utils.communication import send_can_message
from .helper import connect, get_single_response_timeout, return204

from ...schemas.can_commands.system import SystemGoCommand, SystemStopCommand, SystemHaltCommand, SystemResetCommand
from ...schemas.can_commands import AbstractCANMessage, CommandSchema

from .schemas.lok import FunctionValueModel, SpeedModel, DirectionModel

from .configs import get_config

from .schemas.system import *


router = APIRouter()

@router.post("/status", status_code=204)
async def get_status(status: SystemStatus, x_can_hash: str = Header(None)):
    clas = SystemStatusCommand[status.value].value
    id = 0 # all devices
    message = clas(hash_value = x_can_hash, response = False, id=id)
    await send_can_message(message)
