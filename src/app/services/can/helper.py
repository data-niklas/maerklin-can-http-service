import asyncio
import websockets

from collections import defaultdict

from ...schemas.can_commands import AbstractCANMessage
from ..can_recv.converter import type_map

from fastapi import HTTPException, Response

from typing import Tuple
 

from config import get_settings
settings = get_settings()


HOST = settings.can_receiver_host
PORT = settings.can_receiver_port
TIMEOUT = settings.can_timeout

def connect():
    return websockets.connect(f"ws://{HOST}:{PORT}")

def parse_high_level_message(message: str) -> AbstractCANMessage:
    t = message[:message.find("{")]
    payload = message[len(t):]
    clas = type_map[t] # hacky
    return clas.parse_raw(payload)

async def get_single_response(connection, check):
    async for message in connection:
        message = parse_high_level_message(message)
        if not check(message):
            continue
        return message

async def get_single_response_timeout(connection, check, transform_result = None):
    try:
        result = await asyncio.wait_for(get_single_response(connection, check), TIMEOUT/1000)
        if transform_result is None:
            return result
        return transform_result(result)
    except Exception as e:
        print(f"{e}")
        raise HTTPException(status_code=504, detail="CAN timeout exceeded")

def return204(m):
    return Response(status_code=204)

def get_tree():
    return defaultdict(get_tree)

def parse_config(text: str, level: int = -1, line: int = 0) -> Tuple[int, defaultdict]:
    ret = get_tree()

    def level_map(level: int) -> str:
        if level == -1:
            return "["
        assert level >= 0
        return "." * level
    
    def level_from_prefix(text: str) -> int:
        text = text.strip()
        if text[0] == "[":
            assert text[-1] == "]"
            return -1
        for i, c in enumerate(text):
            if c != ".":
                return i
    
    def remove_prefix(text: str) -> str:
        text = text.strip()
        for i, c in enumerate(text):
            if c != ".":
                return text[i:]
    
    lines = text.splitlines()
    line_num = line
    while line_num < len(lines):
        line = lines[line_num]
        print(line, line_num, level, level_from_prefix(line))
        if level_from_prefix(line) < level:
            return (line_num, ret)
        assert level_from_prefix(line) == level
        line = remove_prefix(line)
        if "=" in line:
            ret[line.split("=")[0]] = line.split("=")[1]
            line_num += 1
        else:
            line_num, inner = parse_config(text, level+1, line_num+1)
            if line in ret:
                if isinstance(ret[line], list):
                    ret[line].append(inner)
                else:
                    ret[line] = [ret[line], inner]
            else:
                ret[line] = inner

    return (line_num, ret)
