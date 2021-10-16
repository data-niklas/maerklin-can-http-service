from .tcp import send_async, recv_async
from ..schemas.can import CANMessage
from ..schemas.can_commands.base import AbstractCANMessage

async def send_raw_can_message(message: CANMessage, writer=None):
    data = message.to_bytes()
    return await send_async(data, writer)

async def send_can_message(message: AbstractCANMessage, writer=None):
    message = message.to_can_message()
    return await send_raw_can_message(message)