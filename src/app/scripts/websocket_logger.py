import asyncio
import websockets

HOST = "localhost"
PORT = 8888

async def main():
    messages = list()
    try:
        async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
            print("connected")
            async for message in websocket:
                print(message)
                messages.append(message)
    except Exception as e:
        print(f"stopping with {e}")
    finally:
        with open("messages.log", "a") as f:
            f.write("\n" + "\n".join(messages))

if __name__ == "__main__":
    asyncio.run(main())