import asyncio
import zlib
import websockets
from datetime import datetime, timedelta
import time
import requests
import traceback

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import asc, desc
from sqlalchemy.future import select

from config_wrapper import get_settings

from app.schemas.can import CANMessage as PydanticCANMessage
from app.models.can_message import Base, ConfigMessage, ConfigUsageMessage, ConfigLocomotiveMessage, LocomotiveMetricMessage, LocomotiveSpeedMessage
from app.models.can_message_converter import registered_models, convert_to_model
from app.services.can_recv.converter import type_map as pydantic_type_map
from app.schemas.can_commands import CommandSchema, LocomotiveDirectionCommand, LocomotiveDirection, LocomotiveSpeedCommand
from app.services.can.helper import parse_config

settings = get_settings()

HOST = settings.can_receiver_host
PORT = settings.can_receiver_port

DB = settings.db_dump_database

engine = create_async_engine(
    DB, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def parse_message(message):
    t = message[:message.find("{")]
    payload = message[len(t):]
    clas = pydantic_type_map[t]  # hacky
    abstract_message = clas.parse_raw(payload)
    return abstract_message


async def dump_model(session, abstract_model):
    session.add(abstract_model)
    await session.commit()


async def dump(session, pydantic_abstract_message):
    print("Dumping message")
    abstract_model = convert_to_model(pydantic_abstract_message)
    assert abstract_model is not None
    await dump_model(session, abstract_model)


async def save_usage_message(session, obj, pydantic_abstract_message):
    await dump_model(session, ConfigUsageMessage.from_message(obj, pydantic_abstract_message))


async def save_locomotive_message(session, obj, pydantic_abstract_message):
    for lok in obj["lokomotive"]:
        if not isinstance(lok, dict) or lok.get("name") is None:
            continue # skip empty entries
        await dump_model(session, ConfigLocomotiveMessage.from_message(lok, pydantic_abstract_message))


CONFIG_MESSAGE_DICT = {
    "[verbrauch]": save_usage_message,
    "[lokomotive]": save_locomotive_message
}


async def get_next_config_stream(session, connection):
    async for message in connection:
        pydantic_abstract_message = await parse_message(message)
        if not pydantic_abstract_message.get_command() == CommandSchema.ConfigDataStream:
            await dump(session, pydantic_abstract_message)
            continue
        return pydantic_abstract_message


async def get_next_config_stream_timeout(session, connection):
    try:
        return await asyncio.wait_for(get_next_config_stream(session, connection), 1)
    except Exception as e:
        print(f"{e}")
        return None


async def init_db():
    async with engine.begin() as conn:
        for model in registered_models:
            await conn.run_sync(model.metadata.create_all)



async def save_config_message(session, data, length, pydantic_abstract_message):
    _, config_obj = parse_config(data)

    for message_type in CONFIG_MESSAGE_DICT:
        if message_type in config_obj:
            obj = config_obj[message_type]
            await CONFIG_MESSAGE_DICT[message_type](session, obj, pydantic_abstract_message)

    # also save to normal ConfigMessage
    await dump_model(session, ConfigMessage.from_message(data, length, pydantic_abstract_message))

async def process_config_stream(session, websocket, pydantic_abstract_message):
    if pydantic_abstract_message.file_length is None:
        return
    length = pydantic_abstract_message.file_length
    received_count = 0
    received_data = ""
    while received_count < length:
        next_message = await get_next_config_stream_timeout(session, websocket)
        if next_message is None:
            break
        data = next_message.data
        if not isinstance(data, str):
            break
        if received_count > 0:
            received_data += " "
        received_count += 8
        received_data += data

    data = bytes.fromhex(received_data)[:length]
    try:
        data = zlib.decompress(data[4:])
    except Exception as e:
        pass
    try:
        data = data.decode("utf-8")
    except Exception as e:
        pass

    await save_config_message(session, data, length, pydantic_abstract_message)


async def start_websocket_listener():
    try:
        async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
            async with SessionLocal() as session:
                print("connected")
                async for message in websocket:
                    print(message)
                    pydantic_abstract_message = await parse_message(message)
                    print(pydantic_abstract_message.get_command())
                    if pydantic_abstract_message.get_command() == CommandSchema.ConfigDataStream:
                        await process_config_stream(session, websocket, pydantic_abstract_message)
                    else:
                        await dump(session, pydantic_abstract_message)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except Exception as e:
        traceback.print_exc()
        print(f"restarting websocket listener")
        await start_websocket_listener()

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    loop.run_until_complete(start_websocket_listener())


if __name__ == "__main__":
    main()
