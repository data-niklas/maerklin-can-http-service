from fastapi import APIRouter

from ...utils.communication import send_can_message
from ...schemas.can_commands import LocomotiveSpeedCommand, LocomotiveDirectionCommand, LocomotiveFunctionCommand

router = APIRouter()

@router.post("/speed")
async def loc_speed(message: LocomotiveSpeedCommand):
    await send_can_message(message)
    return {"send_status": "success"}

@router.post("/direction")
async def loc_speed(message: LocomotiveDirectionCommand):
    await send_can_message(message)
    return {"send_status": "success"}

@router.post("/function")
async def loc_speed(message: LocomotiveFunctionCommand):
    await send_can_message(message)
    return {"send_status": "success"}