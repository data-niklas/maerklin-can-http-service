from fastapi import APIRouter

from ...utils.communication import send_raw_can_message
from ...schemas.can import CANMessage

router = APIRouter()

@router.post("/")
async def can_message(message: CANMessage):
    await send_raw_can_message(message)
    return {"send_status": "success"}