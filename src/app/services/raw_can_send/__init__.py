from fastapi import APIRouter, Response

from ...utils.communication import send_raw_can_message
from ...schemas.can import CANMessage

router = APIRouter()

@router.post("/", status_code=204)
async def can_message(message: CANMessage):
    await send_raw_can_message(message)
    return Response(status_code=204)