from fastapi import FastAPI

from tcp import send
from schemas.can import CANMessage

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Testing"}

@app.post("/can")
async def can_message(message: CANMessage):
    await send(message.to_bytes())
    return {"send_status": "success"}