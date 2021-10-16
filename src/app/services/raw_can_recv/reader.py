import json
import asyncio

from fastapi.encoders import jsonable_encoder

from ...schemas.can import CANMessage
from ...utils.communication import recv_raw_can_message

IS_DEBUG_SERVER = True

IP = "127.0.0.1"
PORT = 15731


class BackgroundReader(object):
    def __init__(self, broadcaster):
        self.broadcaster = broadcaster
    
    async def __handle_client(self, reader, writer):
        while True:
            can_message = await recv_raw_can_message(reader)
            if can_message is None:
                if IS_DEBUG_SERVER:
                    # connection was closed
                    return
                # received wrong message
                continue
            
            str_data = json.dumps(jsonable_encoder(can_message))
            
            print(f"got message {str_data}")
            await self.broadcaster.broadcast(str_data)
    
    async def run_main(self):
        print("starting BackgroundReader")
        if IS_DEBUG_SERVER:
            server = await asyncio.start_server(self.__handle_client, IP, PORT)
            async with server:
                await server.serve_forever()
        else:
            reader, writer = await asyncio.open_connection(IP, PORT)
            await handle_client(reader, writer)