from fastapi import FastAPI

from udp import send_recv_udp
from schemas.can import CANMessage

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Testing"}

@app.post("/can", response_model=CANMessage)
async def can_message(message: CANMessage):
    return CANMessage.from_bytes(send_recv_udp(message.to_bytes()))