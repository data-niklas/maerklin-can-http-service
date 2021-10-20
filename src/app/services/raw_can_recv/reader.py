import asyncio


from ...schemas.can import CANMessage
from ...utils.communication import recv_raw_can_message
from ...utils.coding import obj_to_json


IP = "127.0.0.1"
PORT = 15731

class BackgroundReader(object):
    def __init__(self, broadcaster):
        self.broadcaster = broadcaster
    
    async def run_main(self):
        print("starting BackgroundReader")
        reader, writer = await asyncio.open_connection(IP, PORT)
        print("Connected")
        while True:
            can_message = await recv_raw_can_message(reader)
            if can_message is None:
                # received wrong message
                continue
            
            str_data = obj_to_json(can_message)
            
            print(f"got message {str_data}")
            await self.broadcaster.broadcast(str_data)