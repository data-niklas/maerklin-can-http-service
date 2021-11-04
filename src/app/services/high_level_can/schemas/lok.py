from pydantic import BaseModel
from ....schemas.can_commands.loc import *

class DirectionModel(BaseModel):
    direction: LocomotiveDirection

class SpeedModel(BaseModel):
    speed: int

class FunctionValueModel(BaseModel):
    value: int