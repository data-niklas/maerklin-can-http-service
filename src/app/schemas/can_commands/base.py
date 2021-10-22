from pydantic import BaseModel

from ..can import CANMessage, MessageIdentifier, CommandSchema
from ...utils.coding import bytes_to_str


class AbstractCANMessage(BaseModel):
    hash_value: int
    response: bool

    def get_command(self) -> CommandSchema:
        raise Exception("Not implemented, do not use abstract class directly")
    
    def get_data(self) -> bytes:
        raise Exception("Not implemented, do not use abstract class directly")

    def to_can_message(self) -> CANMessage:
        message_identifier = MessageIdentifier(priority=0, command=self.get_command(), response=self.response, hash_value=self.hash_value)
        data = bytes_to_str(self.get_data())
        return CANMessage(message_id = message_identifier, data = data)
    
    def from_can_message(message: CANMessage):
        message_id = message.message_id
        return AbstractCANMessage(hash_value=message_id.hash_value, response=message_id.response)