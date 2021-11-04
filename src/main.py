from fastapi import FastAPI

from app.utils.tcp import send_async

from app.services import raw_can_send
from app.services import high_level_can_send
from app.services import raw_can_recv
from app.services import high_level_can_recv
from app.services import high_level_can


raw_can_sender = FastAPI()
raw_can_sender.include_router(raw_can_send.router)

can_sender = FastAPI()
can_sender.include_router(high_level_can_send.router)

raw_can_receiver = FastAPI()
raw_can_receiver.include_router(raw_can_recv.router)

can_receiver = FastAPI()
can_receiver.include_router(high_level_can_recv.router)

can = FastAPI()
can.include_router(high_level_can.router)