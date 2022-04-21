from fastapi import APIRouter, Header, Response, HTTPException

from typing import Type

from ...schemas.can_commands.general import ParticipantPingCommand
from ...schemas.can_commands import AbstractCANMessage, CommandSchema
from ...utils.communication import send_can_message
from .helper import get_single_response_timeout, connect, return204

from random import randrange

router = APIRouter()

# TODO: Get state through database request

used_hashes = set()

async def try_hash(connection, message, hash):
    global used_hashes
    if hash in used_hashes:
        return False

    def check(m):
        if not m.response or m.get_command() != CommandSchema.ParticipantPing:
            return False
        return True

    await send_can_message(message)
    try:
        while True:
            response = await get_single_response_timeout(connection, check)
            used_hashes.add(response.hash_value)
            if response.hash_value == hash:
                return False
    except HTTPException as e:
        # No new ping response
        used_hashes.add(hash)
        return True

@router.get("/hash")
async def get_hash():
    async with connect() as connection:
        while True:
        # 16 bit random hash
        #hash = randrange(0, 65535)
        #hash |= 0b0000001100000000
        #hash &= 0b1111111101111111 
            hash = randrange(0, 0x10000) & 0xff7f | 0x0300
            message = ParticipantPingCommand(hash_value = hash, response = False)
            if await try_hash(connection, message, hash):
                return hash
            