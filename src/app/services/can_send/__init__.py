from fastapi import APIRouter

from . import loc
from . import system
from . import general
from . import mfx


router = APIRouter()
router.include_router(
    loc.router,
    prefix = "/loc",
    tags = ["loc"]
)
router.include_router(
    system.router,
    prefix = "/system",
    tags = ["system"]
)
router.include_router(
    mfx.router,
    prefix = "/mfx",
    tags = ["mfx"]
)
router.include_router(
    general.router
)