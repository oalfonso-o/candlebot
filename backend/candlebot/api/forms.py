from fastapi import APIRouter

from candlebot.db import db_find
from candlebot import constants

router = APIRouter(
    prefix="/forms",
    tags=["forms"],
    responses={404: {"description": "Not found"}},
)


@router.get("/symbols")
async def get_symbols():
    return sorted(db_find.available_symbols())


@router.get("/symbols/all")
async def get_symbols_all():
    return sorted(constants.TRADING_SYMBOLS)


@router.get("/intervals")
async def get_intervals():
    return sorted(db_find.available_intervals())


@router.get("/intervals/all")
async def get_intervals_all():
    return sorted(constants.INTERVALS)


@router.get("/strategies")
async def get_strategies():
    pass
