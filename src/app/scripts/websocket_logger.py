import asyncio
import websockets

from datetime import datetime

HOST = "localhost"
PORT = 8889

messages = list()

async def main():
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        print("connected")
        async for message in websocket:
            message = str(message)
            print(message)
            messages.append(f"{str(datetime.now())} - {message}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"stopping with {e}")
    except KeyboardInterrupt:
        print("stopping with keyboard interrupt")
        with open("messages.log", "a") as f:
            f.write("\n" + "\n".join(messages))
    finally:
        with open("messages.log", "a") as f:
            f.write("\n" + "\n".join(messages))