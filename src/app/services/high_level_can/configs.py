import zlib
from typing import Type

from fastapi import APIRouter, Header, Response

from ...schemas.can_commands.general import RequestConfigDataCommand
from ...schemas.can_commands import AbstractCANMessage, CommandSchema
from ...utils.communication import send_can_message
from .helper import get_single_response_timeout, connect, return204


router = APIRouter()


@router.get("/{filename}")
async def get_config(filename: str, x_can_hash: str = Header(None)):
    message = RequestConfigDataCommand(filename = filename, hash_value = x_can_hash, response = False)

    def check_response(m):
        if not m.response or m.get_command() != CommandSchema.RequestConfigData:
            return False
        if m.filename != filename:
            return False
        return True

    def check_header(m):
        if m.get_command() != CommandSchema.ConfigDataStream:
            return False
        if m.file_length is None:
            return False
        return True
    
    def check_body(m):
        if m.get_command() != CommandSchema.ConfigDataStream:
            return False
        if m.file_length is not None:
            return False
        return True

    async with connect() as connection:
        await send_can_message(message)
        response =  await get_single_response_timeout(connection, check_response, lambda m: None)
        if response is not None:
            return response
        length = await get_single_response_timeout(connection, check_header, lambda m: m.file_length)
        if not isinstance(length, int):
            return length
        
        received_count = 0
        received_data = ""
        while received_count < length:
            data = await get_single_response_timeout(connection, check_body, lambda m: m.data)
            if not isinstance(data, str):
                return message
            received_count += 8
            if received_count > 0:
                received_data += " "
            received_data += data
        
        data = bytes.fromhex(received_data)[:length]
        decoded = None
        try:
            decompressed = zlib.decompress(data[4:])
            decoded = decompressed.decode("utf-8")
        except:
            try:
                decoded = data.decode("utf-8")
            except:
                pass
        
        return decoded
