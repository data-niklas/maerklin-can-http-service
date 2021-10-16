from .base import AbstractCANMessage
from ..can import CommandSchema
from ...utils.coding import int_to_bytes

class ParticipantPingCommand(AbstractCANMessage):
    sender_id: int = None
    software_version: int = None
    device_id: int = None

    def get_command(self) -> CommandSchema:
        return CommandSchema.ParticipantPing
    
    def get_data(self) -> bytes:
        if self.sender_id is None:
            assert self.software_version is None
            assert self.device_id is None
            return bytes()
        ret = bytes()
        assert self.sender_id is not None
        assert self.software_version is not None
        assert self.device_id is not None

        ret += int_to_bytes(self.sender_id, 4)
        ret += int_to_bytes(self.software_version, 2)
        ret += int_to_bytes(self.device_id, 2)

        return ret
