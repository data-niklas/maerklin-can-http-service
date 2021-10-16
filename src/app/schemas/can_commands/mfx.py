from .base import AbstractCANMessage
from ..can import CommandSchema
from ...utils.coding import int_to_bytes

class AbstractMfxCommand(AbstractCANMessage):
    mfx_uid: int
    mfx_sid: int
    def get_other_data(self) -> bytes:
        raise NotImplentedError()
    
    def get_data(self) -> bytes:
        data = bytes()
        data += int_to_bytes(mfx_uid, 4)
        data += int_to_bytes(mfx_sid, 2)
        data += self.get_other_data()
        return data

class MfxBindCommand(AbstractMfxCommand):
    def get_command(self) -> CommandSchema:
        return CommandSchema.MFXBind

    def get_other_data(self) -> bytes:
        return bytes()

class MfxVerifyCommand(AbstractMfxCommand):
    ask_ratio: int = None
    def get_command(self) -> CommandSchema:
        return CommandSchema.MFXVerify

    def get_other_data(self) -> bytes:
        if ask_ratio:
            return int_to_bytes(ask_ratio, 1)
        return bytes()