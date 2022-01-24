import asyncio
import websockets

from config_wrapper import get_settings
settings = get_settings()

lines = list()

async def echo(websocket, path):
    for line in lines:
        await websocket.send(line)

async def main():
    async with websockets.serve(echo, "localhost", settings.can_receiver_port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    with open("../out/messages.log", "r") as f:
        lines = f.readlines()
    lines = [line[line.find("- ")+2:] for line in lines]
    asyncio.run(main())