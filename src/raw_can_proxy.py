import socket
from schemas.can import CANMessage
from fastapi.encoders import jsonable_encoder
import json
from multiprocessing import Manager, Queue, Process
import websockets
import asyncio

IS_DEBUG_SERVER = True

IP = "127.0.0.1"
PORT = 15731
WS_IP = "127.0.0.1"
WS_PORT = 8888

async def reader(queue):
    print("starting reader")

    async def handle_client(reader, writer):
        while True:
            data = await reader.read(13)
            if len(data) != 13:
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

async def handle_websocket(websocket, path):
    print("started new connection")
    queue = Queue()
    global queues
    async with queues_lock:
        queues.append(queue)
        print(len(queues))
    while not websocket.closed:
        msg = queue.get()
        print("got message")
        await websocket.send(msg)

CLIENTS = set()

async def dumb_handler(websocket, path):
    print("got new connection")
    CLIENTS.add(websocket)
    try:
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
    print("broadcaster")
    loop.create_task(broadcaster(queue))
    print("reader")
    loop.create_task(reader(queue))
    print("server")
    loop.run_until_complete(websockets.serve(dumb_handler, WS_IP, WS_PORT))
    loop.run_forever()
    


if __name__ == "__main__":
    main()