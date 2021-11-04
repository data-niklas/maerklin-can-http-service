from fastapi import APIRouter, Header, Response

from typing import Type

from ...schemas.can_commands.loc import SwitchingAccessoriesCommand
from ...schemas.can_commands import AbstractCANMessage, CommandSchema
from ...utils.communication import send_can_message
from .helper import get_single_response_timeout, connect, return204

from .schemas.accessory import SwitchingAccessoriesModel


router = APIRouter()

# TODO: Get state through database request

@router.post("/{loc_id}", status_code=204)
async def set_accessory(body: SwitchingAccessoriesModel, loc_id: int, x_can_hash: str = Header(None)):
    message = SwitchingAccessoriesCommand(loc_id = loc_id, hash_value = x_can_hash, response = False, **vars(body))

    def check(m):
        if not m.response or m.get_command() != CommandSchema.SwitchingAccessories:
            return False
        if m.value != body.value or m.position != body.position or m.power != body.power:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, return204)