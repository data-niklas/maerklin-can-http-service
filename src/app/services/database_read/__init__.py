from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage, add_pagination
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from odata_query.sqlalchemy import apply_odata_query

from app.models.can_message import Base
from app.models.can_message_converter import registered_models
from config import get_settings

router = APIRouter()

settings = get_settings()

DB = settings.high_level_db_dump_database

engine = create_async_engine(
    DB, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

@router.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        for model in registered_models:
            await conn.run_sync(model.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session

def make_get(model):
    @router.get(f"/get{model.__name__}/", response_model=LimitOffsetPage[sqlalchemy_to_pydantic(model)])
    async def get(filter: Optional[str] = None, db: AsyncSession = Depends(get_db)):
        query = select(model)
        if filter is not None and len(filter) > 0:
            query = apply_odata_query(query, filter)
        return await paginate(db, query)

for model in registered_models:
    make_get(model)

add_pagination(router)