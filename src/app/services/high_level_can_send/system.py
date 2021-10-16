from fastapi import APIRouter

from ...utils.communication import send_can_message
from ...schemas.can_commands import SystemStopCommand, SystemGoCommand
from ...schemas.can_commands import SystemHaltCommand, LocomotiveEmergencyStopCommand, LocomotiveCycleStopCommand

router = APIRouter()

@router.post("/start")
async def system_start(message: SystemGoCommand):
    await send_can_message(message)
    return {"send_status": "success"}

@router.post("/stop")
async def system_start(message: SystemStopCommand):
    await send_can_message(message)
    return {"send_status": "success"}

@router.post("/halt")
async def system_start(message: SystemHaltCommand):
    await send_can_message(message)
    return {"send_status": "success"}

@router.post("/locomotive_emergency_stop")
async def system_start(message: LocomotiveEmergencyStopCommand):
    await send_can_message(message)
    return {"send_status": "success"}

@router.post("/locomotive_cycle_stop")
async def system_start(message: LocomotiveCycleStopCommand):
    await send_can_message(message)
    return {"send_status": "success"}