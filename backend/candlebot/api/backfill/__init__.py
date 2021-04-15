from fastapi import APIRouter

from candlebot.api.backfill import backfill

router = APIRouter(
    prefix="/backfill",
    tags=["backfill"],
    responses={404: {"description": "Not found"}},
)


@router.get("/list")
async def backfill_list():
    return backfill.list_()
