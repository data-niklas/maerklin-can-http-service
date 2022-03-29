from pydantic import BaseModel
from enum import Enum
from ....schemas.can_commands.system import SystemResetCommand, SystemGoCommand, SystemHaltCommand, SystemStopCommand


class SystemStatus(str, Enum):
    STOP = "Stop"
    HALT = "Halt"
    RESET = "Reset"
    GO = "Go"

class SystemStatusCommand(Enum):
    Stop = SystemStopCommand
    Halt = SystemHaltCommand
    Reset = SystemResetCommand
    Go = SystemGoCommand