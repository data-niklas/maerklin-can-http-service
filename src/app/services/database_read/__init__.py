from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from app.models.can_message import Base, LocomotiveSpeedMessage
from app.models.can_message_converter import registered_models
from config import get_settings

router = APIRouter()

settings = get_settings()

DB = settings.high_level_db_dump_database

engine = create_engine(
    DB, connect_args={"check_same_thread": False}
)

for model in registered_models:
    model.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def make_get(model):
    @router.get(f"/get{model.__name__}/", response_model=List[sqlalchemy_to_pydantic(model)])
    def get(db: Session = Depends(get_db)):
        return db.query(model).all()

for model in registered_models:
    make_get(model)
    