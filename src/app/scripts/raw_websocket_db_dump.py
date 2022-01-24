import asyncio
import websockets

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from config_wrapper import get_settings

from app.schemas.can import CANMessage as PydanticCANMessage
from app.models.raw_can_message import CANMessage, Base

settings = get_settings()

HOST = settings.raw_can_receiver_host
PORT = settings.raw_can_receiver_port
DB = settings.raw_db_dump_database

async def dump(session, message):
    print("Dumping message")
    pydantic_can_message = PydanticCANMessage.parse_raw(message)
    can_message = CANMessage.from_schema(pydantic_can_message)
    session.add(can_message)
    session.commit()


async def create_sql_session():
    engine = create_engine(DB)
    Base.metadata.create_all(engine)
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