from sqlalchemy import (
    Column, 
    DateTime,
    Integer,
    Boolean,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CANMessage(Base):
    __tablename__ = 'can_message'
    timestamp = Column(DateTime, primary_key=True)
    priority = Column(Integer, nullable=False)
    command = Column(Text, nullable=False)
    is_response = Column(Boolean, nullable=False)
    hash = Column(Integer, nullable=False)
    data = Column(Text, nullable=False)

    def from_schema(can_message):
        message_id = can_message.message_id
        timestamp = datetime.now()
        priority = message_id.priority
        command = message_id.command.value
        is_response = message_id.response
        hash = message_id.hash_value
        data = can_message.data

        return CANMessage(timestamp=timestamp, priority=priority, command=command, is_response=is_response, hash=hash, data=data)