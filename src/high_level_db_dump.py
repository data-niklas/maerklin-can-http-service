import asyncio
from msilib.schema import Error
import zlib
import websockets

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from app.schemas.can import CANMessage as PydanticCANMessage
from app.models.can_message import Base, ConfigMessage
from app.models.can_message_converter import registered_models, convert_to_model
from app.services.high_level_can_recv.converter import type_map as pydantic_type_map
from app.schemas.can_commands import CommandSchema

from config import get_settings
settings = get_settings()

HOST = settings.can_receiver_host
PORT = settings.can_receiver_port

DB = "sqlite:///high_level_dump.sqlite3"


async def parse_message(message):
    t = message[:message.find("{")]
    payload = message[len(t):]
    clas = pydantic_type_map[t]  # hacky
    abstract_message = clas.parse_raw(payload)
    return abstract_message


async def dump(session, pydantic_abstract_message):
    print("Dumping message")
    abstract_model = convert_to_model(pydantic_abstract_message)
    if pydantic_abstract_message.get_command() == CommandSchema.SystemCommand:
        print(pydantic_abstract_message.get_subcommand())
    assert not abstract_model is None
    session.add(abstract_model)
    session.commit()


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


async def create_sql_session():
    engine = create_engine(DB)
    for model in registered_models:
        model.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


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
        received_count += 8
        if received_count > 0:
            received_data += " "
        received_data += data

    data = bytes.fromhex(received_data)[:length]
    try:
        data = zlib.decompress(data[4:])
    except Exception as e:
        print(f"{e}")
    try:
        data = data.decode("utf-8")
    except Exception as e:
        print(f"{e}")

    session.add(ConfigMessage.from_message(
        data, length, pydantic_abstract_message))


async def main():
    session = await create_sql_session()
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        print("connected")
        async for message in websocket:
            print(message)
            pydantic_abstract_message = await parse_message(message)
            print(pydantic_abstract_message.get_command())
            if pydantic_abstract_message.get_command() == CommandSchema.ConfigDataStream:
                await process_config_stream(session, websocket, pydantic_abstract_message)
            else:
                await dump(session, pydantic_abstract_message)

if __name__ == "__main__":
    asyncio.run(main())
