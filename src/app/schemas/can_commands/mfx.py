from .base import AbstractCANMessage
from ..can import CommandSchema, CANMessage
from ...utils.coding import int_to_bytes, bytes_to_int

class AbstractMfxCommand(AbstractCANMessage):
    mfx_uid: int
    mfx_sid: int

    def get_other_data(self) -> bytes:
        raise NotImplementedError()
    
    def get_data(self) -> bytes:
        data = bytes()
        data += int_to_bytes(self.mfx_uid, 4)
        data += int_to_bytes(self.mfx_sid, 2)
        data += self.get_other_data()
        return data
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        abstract_message = AbstractCANMessage.from_can_message(message)

        data = message.get_data_bytes()
        assert len(data) >= 6

        mfx_uid = bytes_to_int(data[:4])
        mfx_sid = bytes_to_int(data[4:6])

        return AbstractMfxCommand(mfx_uid=mfx_uid, mfx_sid=mfx_sid, **vars(abstract_message))

class MfxBindCommand(AbstractMfxCommand):
    def get_command(self) -> CommandSchema:
        return CommandSchema.MFXBind

    def get_other_data(self) -> bytes:
        return bytes()
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        if message.message_id.command != CommandSchema.MFXBind:
            return None
        abstract_message = AbstractMfxCommand.from_can_message(message)

        
        return MfxBindCommand(**vars(abstract_message))

class MfxVerifyCommand(AbstractMfxCommand):
    ask_ratio: int = None
    def get_command(self) -> CommandSchema:
        return CommandSchema.MFXVerify

    def get_other_data(self) -> bytes:
        if self.ask_ratio is not None:
            return int_to_bytes(self.ask_ratio, 1)
        return bytes()
    
    def from_can_message(message: CANMessage) -> AbstractCANMessage:
        if message.message_id.command != CommandSchema.MFXVerify:
            return None
        abstract_message = AbstractMfxCommand.from_can_message(message)

        
        data = message.get_data_bytes()
        ask_ratio = None
        if len(data) > 6:
            assert len(data) == 7
            ask_ratio = bytes_to_int(data[6:7])
        
        return MfxVerifyCommand(ask_ratio = ask_ratio, **vars(abstract_message))