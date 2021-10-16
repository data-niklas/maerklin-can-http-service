import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...utils.communication import ConnectionManager
from .reader import BackgroundReader


router = APIRouter()
manager = ConnectionManager()
reader = BackgroundReader(manager)

@router.on_event("startup")
async def app_startup():
    asyncio.create_task(reader.run_main())

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)