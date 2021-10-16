import json

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from app.schemas.can import CANMessage

IS_DEBUG_SERVER = True

IP = "127.0.0.1"
PORT = 15731


app = FastAPI()

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
            await connection.send_text(message)

manager = ConnectionManager()

class BackgroundReader(object):
    def __init__(self):
        pass
    
    async def __handle_client(self, reader, writer):
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
            await manager.broadcast(str_data)
    
    async def run_main(self):
        print("starting BackgroundReader")
        if IS_DEBUG_SERVER:
            server = await asyncio.start_server(self.__handle_client, IP, PORT)
            async with server:
                await server.serve_forever()
        else:
            reader, writer = await asyncio.open_connection(IP, PORT)
            await handle_client(reader, writer)

reader = BackgroundReader()

@app.on_event("startup")
async def app_startup():
    asyncio.create_task(reader.run_main())

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)