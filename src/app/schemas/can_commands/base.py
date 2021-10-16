from pydantic import BaseModel

from ..can import CANMessage, MessageIdentifier, CommandSchema


class AbstractCANMessage(BaseModel):
    hash_value: int
    response: bool

    def get_command(self) -> CommandSchema:
        raise Exception("Not implemented, do not use abstract class directly")
    
    def get_data(self) -> bytes:
        raise Exception("Not implemented, do not use abstract class directly")

    def to_can_message(self) -> CANMessage:
        message_identifier = MessageIdentifier(priority=0, command=self.get_command(), response=self.response, hash_value=self.hash_value)
        data = " ".join(f"{byte:02x}" for byte in self.get_data())
        return CANMessage(message_id = message_identifier, data = data)