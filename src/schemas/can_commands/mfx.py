from .base import AbstractCANMessage
from ..can import CommandSchema

class AbstractMfxCommand(AbstractCANMessage):
    mfx_uid: int
    mfx_sid: int
    def get_other_data(self) -> bytes:
        raise NotImplentedError()
    
    def get_data(self) -> bytes:
        data = bytes()
        data += mfx_uid.to_bytes(4, "big")
        data += mfx_sid.to_bytes(2, "big")
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
            return ask_ratio.to_bytes(1, "big")
        return bytes()