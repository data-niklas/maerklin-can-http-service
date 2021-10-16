import asyncio
import json
import socket

import websockets

from app.schemas.can import CANMessage
from fastapi.encoders import jsonable_encoder


IS_DEBUG_SERVER = False

IP = "10.0.0.2"
PORT = 15731
WS_IP = "127.0.0.1"
WS_PORT = 8888

CLIENTS = set()


async def reader(queue):
    print("starting reader")

    async def handle_client(reader, writer):
        while True:
            data = await reader.read(13)
            if len(data) != 13:
                if len(data) == 0 and IS_DEBUG_SERVER:
                    # connection is closed
                    return
                print(f"got wrong message {data} with len {len(data)}")
                continue
            
            can_message = CANMessage.from_bytes(data)
            str_data = json.dumps(jsonable_encoder(can_message))
            print(f"got message {str_data}")
            queue.put_nowait(str_data)

    if IS_DEBUG_SERVER:
        server = await asyncio.start_server(handle_client, IP, PORT)
        async with server:
            await server.serve_forever()
    else:
        reader, writer = await asyncio.open_connection(IP, PORT)
        await handle_client(reader, writer)


async def dumb_handler(websocket, path):
    print("got new connection")
    CLIENTS.add(websocket)
    try:
        # ignore all messages and hold connection
        async for msg in websocket:
            pass
    finally:
        CLIENTS.remove(websocket)


async def broadcaster(queue):
    print("starting broadcaster")
    while True:
        msg = await queue.get()
        websockets.broadcast(CLIENTS, msg)
        queue.task_done()


def main():
    queue = asyncio.Queue()
    
    loop = asyncio.get_event_loop()
    
    loop.create_task(broadcaster(queue))
    loop.create_task(reader(queue))
    loop.run_until_complete(websockets.serve(dumb_handler, WS_IP, WS_PORT))
    
    loop.run_forever()


if __name__ == "__main__":
    main()