import json
import asyncio

from fastapi.encoders import jsonable_encoder

from ...schemas.can import CANMessage
from ...utils.communication import recv_raw_can_message


IP = "127.0.0.1"
PORT = 15731

class BackgroundReader(object):
    def __init__(self, broadcaster):
        self.broadcaster = broadcaster
    
    async def run_main(self):
        print("starting BackgroundReader")
        reader, writer = await asyncio.open_connection(IP, PORT)
        while True:
            can_message = await recv_raw_can_message(reader)
            if can_message is None:
                # received wrong message
                continue
            
            str_data = json.dumps(jsonable_encoder(can_message))
            
            print(f"got message {str_data}")
            await self.broadcaster.broadcast(str_data)