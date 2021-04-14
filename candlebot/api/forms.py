from fastapi import APIRouter

from candlebot.db import db_find

router = APIRouter(
    prefix="/forms",
    tags=["forms"],
    responses={404: {"description": "Not found"}},
)


@router.get("/symbols")
async def get_symbols():
    return db_find.available_symbols


@router.get("/intervals")
async def get_intervals():
    return db_find.available_intervals


@router.get("/strategies")
async def get_strategies():
    pass
