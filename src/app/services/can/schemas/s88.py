from pydantic import BaseModel

class SetS88Model(BaseModel):
    parameter: int

class GetS88Model(BaseModel):
    state_old: int = None 
    state_new: int = None 
    time: int = None 