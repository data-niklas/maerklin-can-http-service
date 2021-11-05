import zlib
import asyncio
import websockets

from app.schemas.can_commands import *
from app.services.high_level_can_recv.converter import type_map

IP = "127.0.0.1"
PORT = 8001

async def main():
    async with websockets.connect(f"ws://{IP}:{PORT}") as websocket:
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