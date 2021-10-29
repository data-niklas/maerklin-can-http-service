import asyncio


from ...schemas.can import CANMessage
from ...utils.communication import recv_raw_can_message
from ...utils.coding import obj_to_json

from config import get_settings
settings = get_settings()

IP = settings.raw_can_ip
PORT = settings.raw_can_port

class BackgroundReader(object):
    def __init__(self, broadcaster):
        self.broadcaster = broadcaster
        self.reader = None
        self.writer = None
    
    async def startup(self):
        print("starting BackgroundReader")
        self.reader, self.writer = await asyncio.open_connection(IP, PORT)
        print("Connected")

    async def run_main(self):
        while True:
            can_message = await recv_raw_can_message(self.reader)
            if can_message is None:
                # received wrong message
                continue

            str_data = obj_to_json(can_message)

            print(f"got message {str_data}")
            await self.broadcaster.broadcast(str_data)