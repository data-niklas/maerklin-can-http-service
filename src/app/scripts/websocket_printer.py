import asyncio
import websockets

from config_wrapper import get_settings
settings = get_settings()

HOST = settings.websocket_printer_host
PORT = settings.websocket_printer_port

async def hello():
    async with websockets.connect(f'ws://{HOST}:{PORT}') as websocket:
        print("connected")
        async for message in websocket:
            print(message)

asyncio.run(hello())