import asyncio
import websockets

lines = list()

async def echo(websocket, path):
    for line in lines:
        await websocket.send(line)

async def main():
    async with websockets.serve(echo, "localhost", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    with open("messages.log", "r") as f:
        lines = f.readlines()
    lines = [line[line.find("- ")+2:] for line in lines]
    asyncio.run(main())