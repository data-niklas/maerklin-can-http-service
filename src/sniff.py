import socket
from schemas.can import CANMessage
from fastapi.encoders import jsonable_encoder
import json

UDP_IP = "127.0.0.1"
UDP_RECEIVE_PORT = 15731
UDP_SEND_PORT = 15730

SEND_RESPONSE = False


recv_sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
recv_sock.bind((UDP_IP, UDP_RECEIVE_PORT))

send_sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP

while True:
    data, addr = recv_sock.recvfrom(1024) # buffer size is 1024 bytes
    if SEND_RESPONSE:
        send_sock.sendto(data, (UDP_IP, UDP_SEND_PORT))
    print(" ".join(f"{byte:02x}" for byte in data))
    can_message = CANMessage.from_bytes(data)
    print(json.dumps(jsonable_encoder(can_message)))