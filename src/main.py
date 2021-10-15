from fastapi import FastAPI

from tcp import send
from schemas.can import CANMessage
from schemas.can_commands import LocomotiveSpeedCommand, LocomotiveDirectionCommand, LocomotiveFunctionCommand
from schemas.can_commands import SystemStopCommand, SystemGoCommand
from schemas.can_commands import ParticipantPingCommand
from schemas.can_commands import SystemHaltCommand, LocomotiveEmergencyStop, LocomotiveCycleStop

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Testing"}

@app.post("/can")
async def can_message(message: CANMessage):
    await send(message.to_bytes())
    return {"send_status": "success"}

@app.post("/api/loc_speed")
async def loc_speed(message: LocomotiveSpeedCommand):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}

@app.post("/api/loc_direction")
async def loc_speed(message: LocomotiveDirectionCommand):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}

@app.post("/api/loc_function")
async def loc_speed(message: LocomotiveFunctionCommand):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}

@app.post("/api/start")
async def system_start(message: SystemGoCommand):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}

@app.post("/api/stop")
async def system_start(message: SystemStopCommand):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}

@app.post("/api/halt")
async def system_start(message: SystemHaltCommand):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}

@app.post("/api/locomotive_emergency_stop")
async def system_start(message: LocomotiveEmergencyStop):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}

@app.post("/api/locomotive_cycle_stop")
async def system_start(message: LocomotiveCycleStop):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}

@app.post("/api/participant_ping")
async def participant_ping(message: ParticipantPingCommand):
    await send(message.to_can_message().to_bytes())
    return {"send_status": "success"}