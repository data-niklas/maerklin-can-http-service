import asyncio
import websockets

from datetime import datetime

from config_wrapper import get_settings
settings = get_settings()

HOST = settings.websocket_logger_host
PORT = settings.websocket_logger_port

messages = list()

async def main():
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        print("connected")
        async for message in websocket:
            message = str(message)
            print(message)
            messages.append(f"{str(datetime.now())} - {message}")

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"need to restart with {repr(e)}")
        except KeyboardInterrupt:
            print("stopping with keyboard interrupt")
            with open("../out/messages.log", "a") as f:
                f.write("\n" + "\n".join(messages))
            break
        finally:
            with open("../out/messages.log", "a") as f:
                f.write("\n" + "\n".join(messages))