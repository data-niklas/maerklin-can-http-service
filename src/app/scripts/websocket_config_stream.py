import zlib
import asyncio
import websockets

from config_wrapper import get_settings

from app.schemas.can_commands import *
from app.services.can_recv.converter import type_map

settings = get_settings()

HOST = settings.raw_can_receiver_host
PORT = settings.raw_can_receiver_port

async def main():
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        print("connected")
        data = str()
        async for message in websocket:
            try:
                t = message[:message.find("{")]
                payload = message[len(t):]
                clas = type_map[t] # hacky
                if t != "ConfigDataStreamCommand":
                    continue
                abstract_message = clas.parse_raw(payload)
                # is config data stream
                if abstract_message.crc is not None:
                    if len(data) > 0:
                        data = bytes.fromhex(data)
                        success = True
                        try:
                            print(data.decode("utf-8"))
                        except:
                            # not a string
                            success = False
                        if not success:
                            try:
                                decompressed = zlib.decompress(data[4:])
                                print(decompressed.decode("utf-8"))
                            except:
                                print("could not decode data")
                    data = str()
                else:
                    if len(data) > 0:
                        data += " "
                        data += abstract_message.data
                    else:
                        data = abstract_message.data
            except Exception as e:
                print(e)

if __name__ == "__main__":
    asyncio.run(main())
