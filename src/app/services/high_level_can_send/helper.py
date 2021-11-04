from typing import Type
from fastapi import Response
from ...schemas.can_commands import AbstractCANMessage
from ...utils.communication import send_can_message

#def transform_name(name: str):
#    return name.lower().replace("command", "")

def create_endpoint(app, name: str, schema : Type[AbstractCANMessage]):
    @app.post(f"/" + name, status_code=204)
    async def post(message: schema):
        await send_can_message(message)
        return Response(status_code=204)