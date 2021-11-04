import asyncio
import websockets

from ...schemas.can_commands import AbstractCANMessage
from ..high_level_can_recv.converter import type_map

from fastapi import HTTPException
 

from config import get_settings
settings = get_settings()


HOST = settings.can_receiver_host
PORT = settings.can_receiver_port
TIMEOUT = settings.can_timeout

def connect():
    return websockets.connect(f"ws://{HOST}:{PORT}")

def parse_high_level_message(message: str) -> AbstractCANMessage:
    t = message[:message.find("{")]
    payload = message[len(t):]
    clas = type_map[t] # hacky
    return clas.parse_raw(payload)

async def get_single_response(connection, check):
    async for message in connection:
        message = parse_high_level_message(message)
        if not check(message):
            continue
        return message

async def get_single_response_timeout(connection, check, transform_result = None):
    try:
        result = await asyncio.wait_for(get_single_response(connection, check), TIMEOUT/1000)
        if transform_result is None:
            return result
        return transform_result(result)
    except Exception as e:
        raise HTTPException(status_code=504, detail="CAN timeout exceeded")