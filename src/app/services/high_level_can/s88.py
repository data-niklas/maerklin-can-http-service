from fastapi import APIRouter, Header, Response

from typing import Type

from ...schemas.can_commands.general import S88EventCommand
from ...schemas.can_commands import AbstractCANMessage, CommandSchema
from ...utils.communication import send_can_message
from .helper import get_single_response_timeout, connect, return204

from .schemas.s88 import SetS88Model, GetS88Model


router = APIRouter()


@router.get("/{device_id}/{contact_id}", response_model=GetS88Model)
async def get_s88(device_id: int, contact_id: int, x_can_hash: str = Header(None)):
    message = S88EventCommand(device_id = device_id, contact_id = contact_id, hash_value = x_can_hash, response = False)

    def check(m):
        if not m.response or m.get_command() != CommandSchema.S88Event:
            return False
        if m.device_id != device_id or m.contact_id != contact_id:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, lambda m: GetS88Model(state_old = m.state_old, state_new = m.state_new, time = m.time))

@router.post("/{device_id}/{contact_id}", status_code=204)
async def set_s88(body: SetS88Model, device_id: int, contact_id: int, x_can_hash: str = Header(None)):
    message = S88EventCommand(device_id = device_id, contact_id = contact_id, hash_value = x_can_hash, response = False, **vars(body))

    def check(m):
        if not m.response or m.get_command() != CommandSchema.S88Event:
            return False
        if m.device_id != device_id or m.contact_id != contact_id:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, return204)