import asyncio
from datetime import datetime, timedelta
import time
import requests
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import asc, desc
from sqlalchemy.future import select

from config_wrapper import get_settings

from app.models.can_message_converter import registered_models
from app.schemas.can_commands import CommandSchema, LocomotiveDirectionCommand, LocomotiveDirection, LocomotiveSpeedCommand


settings = get_settings()

CAN_BASE_URL = f"http://{settings.can_host}:{settings.can_port}/"
CAN_GET_HASH = CAN_BASE_URL + "general/hash"
CAN_LOC_LIST = CAN_BASE_URL + "lok/list"

CAN_SENDER_BASE_URL = f"http://{settings.can_sender_host}:{settings.can_sender_port}/"
CAN_SENDER_GET_LOC_SPEED = CAN_SENDER_BASE_URL + "loc/speed"
CAN_SENDER_GET_LOC_DIRECTION = CAN_SENDER_BASE_URL + "loc/direction"

DB = settings.db_dump_database
engine = create_async_engine(
    DB, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        for model in registered_models:
            await conn.run_sync(model.metadata.create_all)


async def refresh_loc_information():
    locs = get_locs()
    if locs is None:
        print("Got no locs")
        return
    for loc in locs:
        loc_id = loc["loc_id"]

        direction_command = LocomotiveDirectionCommand(direction=None, loc_id=loc_id, response=False, hash_value=get_hash())
        speed_command = LocomotiveSpeedCommand(speed=None, loc_id=loc_id, response=False, hash_value=get_hash())

        requests.post(CAN_SENDER_GET_LOC_DIRECTION, data=direction_command.json())
        requests.post(CAN_SENDER_GET_LOC_SPEED, data=speed_command.json())


@lru_cache
def get_hash():
    return str(requests.get(CAN_GET_HASH).json())


def get_locs():
    res = requests.get(CAN_LOC_LIST, headers={'x-can-hash': get_hash()}).json()
    if isinstance(res, list):
        return res
    return None


async def start_refresher():
    print("started refresher")
    last = datetime.now()
    refresh_interval = settings.refresh_interval
    refresh_delta = timedelta(seconds = refresh_interval)
    while True:
        now = datetime.now()
        elapsed_seconds = (now - last).total_seconds()
        if now < last or elapsed_seconds < refresh_interval:
            remaining = refresh_interval - elapsed_seconds
            print(remaining)
            await asyncio.sleep(remaining)
            continue
        start = last
        end = last + refresh_delta
        await refresh_loc_information()
        last = end


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    loop.run_until_complete(start_refresher())

if __name__ == "__main__":
    main()
