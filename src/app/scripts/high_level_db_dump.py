import asyncio
import zlib
import websockets

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker

from config_wrapper import get_settings

from app.schemas.can import CANMessage as PydanticCANMessage
from app.models.can_message import Base, ConfigMessage, ConfigUsageMessage, ConfigLocomotiveMessage
from app.models.can_message_converter import registered_models, convert_to_model
from app.services.high_level_can_recv.converter import type_map as pydantic_type_map
from app.schemas.can_commands import CommandSchema
from app.services.high_level_can.helper import parse_config

settings = get_settings()

HOST = settings.can_receiver_host
PORT = settings.can_receiver_port

DB = settings.high_level_db_dump_database

engine = create_async_engine(
    DB, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def save_usage_message(session, obj, pydantic_abstract_message):
    session.add(ConfigUsageMessage.from_message(obj, pydantic_abstract_message))

def save_locomotive_message(session, obj, pydantic_abstract_message):
    for lok in obj["lokomotive"]:
        session.add(ConfigLocomotiveMessage.from_message(lok, pydantic_abstract_message))

config_message_dict = dict()
config_message_dict["[verbrauch]"] = save_usage_message
config_message_dict["[lokomotive]"] = save_locomotive_message

async def parse_message(message):
    t = message[:message.find("{")]
    payload = message[len(t):]
    clas = pydantic_type_map[t]  # hacky
    abstract_message = clas.parse_raw(payload)
    return abstract_message


async def dump(session, pydantic_abstract_message):
    print("Dumping message")
    abstract_model = convert_to_model(pydantic_abstract_message)
    assert abstract_model is not None
    session.add(abstract_model)
    await session.commit()


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
    global config_message_dict
    _, config_obj = parse_config(data)

    for message_type in config_message_dict:
        if message_type in config_obj:
            obj = config_obj[message_type]
            config_message_dict[message_type](session, obj, pydantic_abstract_message)
            return

    # fallback
    session.add(ConfigMessage.from_message(
        data, length, pydantic_abstract_message))

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



async def main():
    await init_db()
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

if __name__ == "__main__":
    asyncio.run(main())
