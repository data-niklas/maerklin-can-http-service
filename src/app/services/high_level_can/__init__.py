from fastapi import APIRouter

from . import loc

router = APIRouter()
router.include_router(
    loc.router,
    prefix = "/loc",
    tags = ["loc"]
)