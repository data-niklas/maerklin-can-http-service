import asyncio
import websockets

from ...schemas.can import CANMessage
from ...utils.coding import obj_to_json
from .converter import convert_to_abstract

from config import get_settings
settings = get_settings()

HOST = settings.raw_can_receiver_host
PORT = settings.raw_can_receiver_port

class BackgroundReader(object):
    def __init__(self, broadcaster):
        self.broadcaster = broadcaster
        self.connection = None
    
    async def connect(self):
        return await websockets.connect(f"ws://{HOST}:{PORT}")

    async def startup(self):
        print("starting BackgroundReader")
        self.connection = await self.connect()
        print("Connected")

    async def run_main(self):
        while True:
            try:
                async for message in self.connection:
                    can_message = CANMessage.parse_raw(message)
                    abstract_message = convert_to_abstract(can_message)
                    if abstract_message is None:
                        print(f"got wrong message {can_message}")
                    else:
                        type_name = type(abstract_message).__name__
                        str_data = type_name + obj_to_json(abstract_message)
                        print(f"got message {str_data}")

                        await self.broadcaster.broadcast(str_data)
            except websockets.ConnectionClosed:
                self.connection = await self.connect()
                print("Reconnected")
                continue