from .base import AbstractCANMessage
from ..can import CommandSchema


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

        ret += self.sender_id.to_bytes(4, "big")
        ret += self.software_version.to_bytes(2, "big")
        ret += self.device_id.to_bytes(2, "big")

        return ret