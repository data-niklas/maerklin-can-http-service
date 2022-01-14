from can_message import AbstractCANMessage
from app.schemas.can_commands import AbstractCANMessage as PydanticAbstractCANMessage
registered_models = list()

def convert_to_model(t: str, message: PydanticAbstractCANMessage) -> AbstractCANMessage:
    for model in registered_models:
        abstract_message = model.from_schema(t, message)
        if abstract_message is not None:
            return abstract_message
    return None