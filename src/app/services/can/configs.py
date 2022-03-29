import zlib
from typing import Type, List

from fastapi import APIRouter, Header, Response

from ...schemas.can_commands.general import RequestConfigDataCommand
from ...schemas.can_commands import AbstractCANMessage, CommandSchema
from ...utils.communication import send_can_message
from .helper import get_single_response_timeout, connect, return204, parse_config


router = APIRouter()


async def get_config(request: List[str], hash_value: str, is_binary = False, is_compressed = False, is_config = False):
    request_messages = [RequestConfigDataCommand(filename = s, hash_value = hash_value, response = False) for s in request]

    def check_response(m):
        if not m.response or m.get_command() != CommandSchema.RequestConfigData:
            return False
        if m.filename != request_messages[-1].filename:
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
        for message in request_messages:
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
        if is_compressed:
            data = zlib.decompress(data[4:])
        if not is_binary:
            data = data.decode("utf-8")
            if is_config:
                _, data = parse_config(data)
        return data

@router.get("/lokinfo/{loc_name}")
async def get_lokinfo(loc_name: str = "", x_can_hash: str = Header(None)):
    loc_name = loc_name[:16]
    packet1 = loc_name[:8]
    packet2 = loc_name[8:]
    return await get_config(["lokinfo", packet1, packet2], x_can_hash, is_config=True)

@router.get("/loknamen")
async def get_loknamen(offset: int = 0, limit: int = 5, x_can_hash: str = Header(None)):
    query_str = f"{offset} {limit}"
    return await get_config(["loknamen", query_str], x_can_hash)

@router.get("/maginfo")
async def get_maginfo(offset: int = 0, limit: int = 5, x_can_hash: str = Header(None)):
    query_str = f"{offset} {limit}"
    return await get_config(["maginfo", query_str], x_can_hash, is_config=True)

# TODO: needs parameter
@router.get("/lokdb")
async def get_lokdb(x_can_hash: str = Header(None)):
    return await get_config(["lokdb"], x_can_hash, is_binary=True)

# TODO: needs parameter
@router.get("/lang")
async def get_lang(x_can_hash: str = Header(None)):
    return await get_config(["lang"], x_can_hash, is_binary=True)

@router.get("/ldbver")
async def get_ldbver(x_can_hash: str = Header(None)):
    return await get_config(["ldbver"], x_can_hash)

@router.get("/langver")
async def get_langver(x_can_hash: str = Header(None)):
    return await get_config(["langver"], x_can_hash)

@router.get("/loks")
async def get_loks(x_can_hash: str = Header(None)):
    return await get_config(["loks"], x_can_hash, is_compressed=True, is_config=True)

@router.get("/mags")
async def get_mags(x_can_hash: str = Header(None)):
    return await get_config(["mags"], x_can_hash, is_compressed=True, is_config=True)

@router.get("/gbs")
async def get_gbs(x_can_hash: str = Header(None)):
    return await get_config(["gbs"], x_can_hash, is_compressed=True, is_config=True)

@router.get("/gbs/{index}")
async def get_gbs_page(index: int, x_can_hash: str = Header(None)):
    return await get_config([f"gbs-{index}"], x_can_hash, is_compressed=True, is_config=True)

@router.get("/fs")
async def get_fs(x_can_hash: str = Header(None)):
    return await get_config(["fs"], x_can_hash, is_compressed=True, is_config=True)

@router.get("/lokstat")
async def get_lokstat(x_can_hash: str = Header(None)):
    return await get_config(["lokstat"], x_can_hash, is_compressed=True, is_config=True)

@router.get("/magstat")
async def get_magstat(x_can_hash: str = Header(None)):
    return await get_config(["magstat"], x_can_hash, is_compressed=True, is_config=True)

@router.get("/gbsstat")
async def get_gbsstat(x_can_hash: str = Header(None)):
    return await get_config(["gbsstat"], x_can_hash, is_compressed=True, is_config=True)
