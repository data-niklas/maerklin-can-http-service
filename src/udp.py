import socket
from asyncio import Lock


UDP_IP = "127.0.0.1"
UDP_RECEIVE_PORT = 15730
UDP_SEND_PORT = 15731

udp_lock = Lock()

async def send_recv_udp(message):
    async with udp_lock:
        send_sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        recv_sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
        recv_sock.bind((UDP_IP, UDP_RECEIVE_PORT))

        send_sock.sendto(message, (UDP_IP, UDP_SEND_PORT))

        data, addr = recv_sock.recvfrom(1024) # buffer size is 1024 bytes

        send_sock.close()

        recv_sock.close()

    return data