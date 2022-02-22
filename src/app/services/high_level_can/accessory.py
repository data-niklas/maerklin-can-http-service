from fastapi import APIRouter, Header, Response

from typing import Type

from ...schemas.can_commands.loc import SwitchingAccessoriesCommand
from ...schemas.can_commands import AbstractCANMessage, CommandSchema
from ...utils.communication import send_can_message
from .helper import get_single_response_timeout, connect, return204

from .schemas.accessory import SwitchingAccessoriesModel

from .configs import get_config


router = APIRouter()

# TODO: Get state through database request

@router.post("/{loc_id}", status_code=204)
async def set_accessory(body: SwitchingAccessoriesModel, loc_id: int, x_can_hash: str = Header(None)):
    message = SwitchingAccessoriesCommand(loc_id = loc_id, hash_value = x_can_hash, response = False, **vars(body))

    def check(m):
        if not m.response or m.get_command() != CommandSchema.SwitchingAccessories:
            return False
        if m.value != body.value or m.position != body.position or m.power != body.power:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        return await get_single_response_timeout(connection, check, return204)


@router.get("/list")
async def list_mags(x_can_hash: str = Header(None)):
    def mag_loc_id(dectyp, id):
        id = int(id, 0)
        if dectyp == "mm2":
            return id + 0x3000 - 1 # Taken from the Märklin documentation. See 1.3.1.2 Einbindung bestehender Gleisprotokolle, Bildung der „Loc-ID“
        else:
            return id

    mags_config = await get_config(["mags"], x_can_hash, is_compressed=True, is_config=True)
    mags_list = mags_config["[magnetartikel]"]["artikel"]
    for mag in mags_list:
        mag["loc_id"] = mag_loc_id(mag["dectyp"], mag["id"])
    return mags_list
