from fastapi import APIRouter

from ...utils.communication import send_can_message
from app.schemas.can_commands import ParticipantPingCommand


router = APIRouter()

@router.post("/participant_ping")
async def participant_ping(message: ParticipantPingCommand):
    await send_can_message(message)
    return {"send_status": "success"}