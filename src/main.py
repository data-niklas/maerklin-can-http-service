from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.tcp import send_async

from app.services import raw_can_send
from app.services import high_level_can_send
from app.services import raw_can_recv
from app.services import high_level_can_recv
from app.services import high_level_can
from app.services import database_read as database_read_module


def get_base():
    base = FastAPI()
    base.add_middleware(CORSMiddleware, \
                        allow_origins=["*"], \
                        allow_credentials=True, \
                        allow_methods=["*"], \
                        allow_headers=["*"])
    return base

raw_can_sender = get_base()
raw_can_sender.include_router(raw_can_send.router)

can_sender = get_base()
can_sender.include_router(high_level_can_send.router)

raw_can_receiver = get_base()
raw_can_receiver.include_router(raw_can_recv.router)

can_receiver = get_base()
can_receiver.include_router(high_level_can_recv.router)

can = get_base()
can.include_router(high_level_can.router)

database_read = get_base()
database_read.include_router(database_read_module.router)
