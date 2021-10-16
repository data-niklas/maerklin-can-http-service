import socket

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