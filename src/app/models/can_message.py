from sqlalchemy import (
    Column, 
    DateTime,
    Integer,
    Boolean,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import List


Base = declarative_base()

class AbstractCANMessage(Base):
    timestamp = Column(DateTime, primary_key=True)
    hash_value = Column(Integer, primary_key=True)
    response = Column(Boolean, primary_key=True)

    def from_schema(t, can_message):
        timestamp = datetime.now()
        hash_value = can_message.hash_value
        response = can_message.response

        return AbstractCANMessage(timestamp, hash_value, response)

class AbstractLocomotiveMessage(AbstractCANMessage):
    loc_id = Column(Integer, primary_key=True)

    def from_schema(t, can_message):
        abstract_message = AbstractCANMessage.from_schema(t, can_message)
        loc_id = can_message.loc_id
        return AbstractLocomotiveMessage(loc_id = loc_id, **vars(abstract_message))

class LocomotiveSpeedMessage(AbstractLocomotiveMessage):
    __tablename__ = 'locomotive_speed'
    speed = Column(Integer, nullable=False)

    def from_schema(t, can_message):
        if not t == "LocomotiveSpeedCommand":
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(t, can_message)
        speed = can_message.speed

        return LocomotiveSpeedMessage(speed = speed, **vars(locomotive_message))

class LocomotiveDirectionMessage(AbstractLocomotiveMessage):
    __tablename__ = 'locomotive_direction'
    direction = Column(Text, nullable=False)

    def from_schema(t, can_message):
        if not t == "LocomotiveDirectionCommand":
           return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(t, can_message)
        direction = can_message.direction.value

        return LocomotiveDirectionMessage(direction = direction, **vars(locomotive_message))

class LocomotiveFunctionMessage(AbstractLocomotiveMessage):
    __tablename__ = 'locomotive_function'
    function: Column(Integer, nullable=False)
    value: Column(Integer)
    function_value: Column(Integer)

    def from_schema(t, can_message):
        if not t == "LocomotiveFunctionCommand":
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(t, can_message)
        function = can_message.function
        value = can_message.value
        function_value = can_message.function_value

        return LocomotiveFunctionMessage(function = function, value = value, function_value = function_value, **vars(locomotive_message))




class SwitchingAccessoriesMessage(AbstractLocomotiveMessage):
    __tablename__ = 'switching_accessories'
    position: Column(Integer, nullable=False)
    power: Column(Integer, nullable=False)
    value: Column(Integer)

    def from_schema(t, can_message):
        if not t == "SwitchingAccessoriesCommand":
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(t, can_message)
        position = can_message.position
        power = can_message.power
        value = can_message.value

        return SwitchingAccessoriesMessage(position = position, power = power, value = value, **vars(locomotive_message))


class S88PollingMessage(AbstractLocomotiveMessage):
    __tablename__ = 's88_polling'
    module_count: Column(Integer)
    module: Column(Integer)
    state: Column(Integer)

    def from_schema(t, can_message):
        if not t == "S88PollingCommand":
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(t, can_message)
        module_count = can_message.module_count
        module = can_message.module
        state = can_message.state

        return S88PollingMessage(module_count = module_count, module = module, state = state, **vars(locomotive_message))




class AbstractSystemMessage(AbstractCANMessage):
    id = Column(Integer, primary_key=True)

    def from_schema(t, can_message):
        abstract_message = AbstractCANMessage.from_schema(t, can_message)
        id = can_message.id
        return AbstractSystemMessage(id = id, **vars(abstract_message))

class SystemStatusMessage(AbstractSystemMessage):
    __tablename__ = 'system_status'
    status = Column(Text, nullable=False)

    def from_schema(t, can_message):
        if not t in ["SystemStopCommand", "SystemGoCommand", "SystemHaltCommand"]:
            return None

        abstract_message = AbstractSystemMessage.from_schema(t, can_message)
        
        status = ""
        if t == "SystemStopCommand":
            status = "stop"
        elif t == "SystemGoCommand":
            status = "go"
        elif t == "SystemHaltCommand":
            status = "halt"
        assert not status == ""

        return SystemStatusMessage(status = status, **vars(abstract_message))


