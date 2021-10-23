from fastapi import APIRouter

from ...schemas.can_commands.mfx import *
from .helper import create_endpoint

router = APIRouter()
create_endpoint(router, "bind", MfxBindCommand)
create_endpoint(router, "verify", MfxVerifyCommand)