import asyncio
import websockets

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from app.schemas.can import CANMessage as PydanticCANMessage
from app.models.can_message import Base
from app.models.can_message_converter import registered_models, convert_to_model
from app.services.high_level_can_recv.converter import type_map as pydantic_type_map


from config import get_settings
settings = get_settings()

HOST = settings.can_receiver_host
PORT = settings.can_receiver_port

DB = "sqlite:///high_level_dump.sqlite3"


async def parse_message(message):
    t = message[:message.find("{")]
    payload = message[len(t):]
    clas = pydantic_type_map[t] # hacky
    abstract_message = clas.parse_raw(payload)
    return t, abstract_message

async def dump(session, message):
    print("Dumping message")
    t, pydantic_abstract_message = await parse_message(message)
    abstract_model = convert_to_model(t, pydantic_abstract_message)
    assert not abstract_model is None
    session.add(abstract_model)
    session.commit()


async def create_sql_session():
    engine = create_engine(DB)
    for model in registered_models:
        model.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

async def main():
    session = await create_sql_session()
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        print("connected")
        async for message in websocket:
            print(message)
            await dump(session, message)

if __name__ == "__main__":
    asyncio.run(main())