import socket
import asyncio

IP = "127.0.0.1"
PORT = 15731

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
    if writer is None:
        _, writer = await asyncio.open_connection(IP, PORT)

    writer.write(message)
    await writer.drain()
    
    writer.close()
    await writer.wait_closed()

async def recv_async(message, reader=None):
    if reader is None:
        reader, _ = await asyncio.open_connection(IP, PORT)

    data = await reader.read(13)

    reader.close()

    return data