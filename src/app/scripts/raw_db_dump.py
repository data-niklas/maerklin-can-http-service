import asyncio
import websockets

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
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
    await session.commit()


async def create_sql_session():
    engine = create_async_engine(
        DB, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)
    return SessionLocal()


async def listen_and_dump(session):
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        print("connected")
        async for message in websocket:
            print(message)
            await dump(session, message)

async def main():
    async with await create_sql_session() as session:
        while True:
            try:
                await listen_and_dump(session)
            except KeyboardInterrupt:
                print("KeyboardInterrupt")
                break
            except Exception as e:
                print(f"Error: {repr(e)}")
        

if __name__ == "__main__":
    asyncio.run(main())