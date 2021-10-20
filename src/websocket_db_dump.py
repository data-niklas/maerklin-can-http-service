import asyncio
import websockets

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from app.schemas.can import CANMessage as PydanticCANMessage
from app.models.raw_can_message import CANMessage, Base

IP = "127.0.0.1"
PORT = 8888
DB = "sqlite:///test.sqlite3"

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
    async with websockets.connect(f"ws://{IP}:{PORT}") as websocket:
        print("connected")
        async for message in websocket:
            print(message)
            await dump(session, message)

if __name__ == "__main__":
    asyncio.run(main())