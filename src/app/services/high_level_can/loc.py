from fastapi import APIRouter, Header

from ...schemas.can_commands.loc import *
from typing import Type
from ...schemas.can_commands import AbstractCANMessage
from ...utils.communication import send_can_message
from .helper import *

from .schemas.loc import *




router = APIRouter()

@router.get("/{loc_id}/speed")
async def get_speed(loc_id: int, x_can_hash: str = Header(None)):
    message = LocomotiveSpeedCommand(loc_id = loc_id, hash_value = x_can_hash, response = False)

    def check(m):
        if not m.response or m.get_command() != CommandSchema.LocomotiveSpeed:
            return False
        if m.loc_id != loc_id or m.speed is None:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, lambda m: m.speed)

@router.post("/{loc_id}/speed", status_code=204)
async def set_speed(loc_id: int, speed: SpeedModel, x_can_hash: str = Header(None)):
    message = LocomotiveSpeedCommand(loc_id = loc_id, speed = speed.speed, hash_value = x_can_hash, response = False)

    def check(m):
        if not m.response or m.get_command() != CommandSchema.LocomotiveSpeed:
            return False
        if m.loc_id != loc_id or m.speed != speed.speed:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, lambda m: None)


@router.get("/{loc_id}/direction")
async def get_direction(loc_id: int, x_can_hash: str = Header(None)):
    message = LocomotiveDirectionCommand(loc_id = loc_id, hash_value = x_can_hash, response = False)

    def check(m):
        if not m.response or m.get_command() != CommandSchema.LocomotiveDirection:
            return False
        if m.loc_id != loc_id or m.direction is None:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, lambda m: m.direction.value)


@router.post("/{loc_id}/direction", status_code=204)
async def set_direction(loc_id: int, direction: DirectionModel, x_can_hash: str = Header(None)):
    message = LocomotiveDirectionCommand(loc_id = loc_id, direction = direction.direction, hash_value = x_can_hash, response = False)

    def check(m):
        if not m.response or m.get_command() != CommandSchema.LocomotiveDirection:
            return False
        if m.loc_id != loc_id or m.direction != direction.direction:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, lambda m: None)


@router.get("/{loc_id}/function/{function}")
async def get_function(loc_id: int, function: int, x_can_hash: str = Header(None)):
    message = LocomotiveFunctionCommand(loc_id = loc_id, function = function, hash_value = x_can_hash, response = False)

    def check(m):
        if not m.response or m.get_command() != CommandSchema.LocomotiveFunction:
            return False
        if m.loc_id != loc_id or m.value is None:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, lambda m: m.value)


@router.post("/{loc_id}/function/{function}", status_code=204)
async def set_function(loc_id: int, function: int, value: FunctionValueModel, x_can_hash: str = Header(None)):
    message = LocomotiveFunctionCommand(loc_id = loc_id, function = function, value = value.value, hash_value = x_can_hash, response = False)

    def check(m):
        if not m.response or m.get_command() != CommandSchema.LocomotiveFunction:
            return False
        if m.loc_id != loc_id or m.value != value.value:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, lambda m: None)