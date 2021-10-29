import socket
import asyncio
from config import get_settings
settings = get_settings()
IP = settings.raw_can_ip
PORT = settings.raw_can_port

async def send(message):
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)
    sock.connect((IP, PORT))

    sock.sendall(message)

    sock.close()

async def recv():
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)
    sock.connect((IP, PORT))
    
    data = sock.recv(13)
    
    sock.close()

    return data

async def send_async(message, writer=None):
    got_writer = True
    if writer is None:
        got_writer = False
        _, writer = await asyncio.open_connection(IP, PORT)

    writer.write(message)
    await writer.drain()
    
    if not got_writer:
        writer.close()
    await writer.wait_closed()

async def recv_async(reader=None):
    got_reader = True
    if reader is None:
        got_reader = False
        reader, writer = await asyncio.open_connection(IP, PORT)

    data = await reader.read(13)

    if not got_reader:
        writer.close()
        await writer.wait_closed()

    return data