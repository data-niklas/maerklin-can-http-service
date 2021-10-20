from fastapi import WebSocket

from .tcp import send_async, recv_async
from ..schemas.can import CANMessage
from ..schemas.can_commands.base import AbstractCANMessage

async def send_raw_can_message(message: CANMessage, writer=None):
    data = message.to_bytes()
    return await send_async(data, writer)

async def send_can_message(message: AbstractCANMessage, writer=None):
    message = message.to_can_message()
    return await send_raw_can_message(message)

async def recv_raw_can_message(reader=None) -> CANMessage:
    data = await recv_async(reader)
    if len(data) != 13:
        return None
    return CANMessage.from_bytes(data)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass