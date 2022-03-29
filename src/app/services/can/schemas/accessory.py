from pydantic import BaseModel

class SwitchingAccessoriesModel(BaseModel):
    position: int
    power: int
    value: int = None # time or special value. Time: t*10 ms