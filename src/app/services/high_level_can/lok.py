from fastapi import APIRouter, Header
from typing import Type

from ...utils.communication import send_can_message
from .helper import connect, get_single_response_timeout, return204

from ...schemas.can_commands.loc import LocomotiveSpeedCommand, LocomotiveDirectionCommand, LocomotiveFunctionCommand
from ...schemas.can_commands import AbstractCANMessage, CommandSchema

from .schemas.lok import FunctionValueModel, SpeedModel, DirectionModel

from .configs import get_config


router = APIRouter()

@router.get("/{loc_id}/speed", response_model=SpeedModel)
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
        return await get_single_response_timeout(connection, check, lambda m: SpeedModel(speed=m.speed))

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
        return await get_single_response_timeout(connection, check, return204)


@router.get("/{loc_id}/direction", response_model=DirectionModel)
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
        return await get_single_response_timeout(connection, check, lambda m: DirectionModel(direction=m.direction.value))


@router.post("/{loc_id}/direction", status_code=204)
async def set_direction(loc_id: int, direction: DirectionModel, x_can_hash: str = Header(None)):
    message = LocomotiveDirectionCommand(loc_id = loc_id, direction = direction.direction, hash_value = x_can_hash, response = False)

    def check(m):
        if not m.response or m.get_command() != CommandSchema.LocomotiveDirection:
            return False
        if m.loc_id != loc_id or m.direction is None:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, return204)


@router.get("/{loc_id}/function/{function}", response_model=FunctionValueModel)
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
        return await get_single_response_timeout(connection, check, lambda m: FunctionValueModel(value=m.value))


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
        return await get_single_response_timeout(connection, check, return204)


@router.get("/list")
async def list_locs(x_can_hash: str = Header(None)):
    loks_config = await get_config(["loks"], x_can_hash, is_compressed=True, is_config=True)
    loks_list = loks_config["[lokomotive]"]["lokomotive"]
    for lok in loks_list:
        lok["loc_id"] = int(lok["uid"], 0)
    return loks_list
