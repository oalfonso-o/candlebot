from fastapi import APIRouter

from candlebot.api.strategies import ema
from candlebot.api.strategies import engulfing
from candlebot.api.strategies import triangle
from candlebot.api.strategies import scalping
from candlebot.api.strategies import scalping_ema_10_20

router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
    responses={404: {"description": "Not found"}},
)


@router.get("/ema")
async def strategy_ema(
    date_from=None, date_to=None, symbol='ADAUSDT', interval='1d'
):
    return ema.calc(date_from, date_to, symbol, interval)


@router.get("/engulfing")
async def strategy_engulfing(
    date_from=None, date_to=None, symbol='ADAUSDT', interval='1d'
):
    return engulfing.calc(date_from, date_to, symbol, interval)


@router.get("/scalping")
async def strategy_scalping(
    date_from=None, date_to=None, symbol='ADAUSDT', interval='1d'
):
    return scalping.calc(date_from, date_to, symbol, interval)


@router.get("/scalping_ema_10_20")
async def strategy_scalping_ema_10_20(
    date_from=None, date_to=None, symbol='ADAUSDT', interval='1d'
):
    return scalping_ema_10_20.calc(date_from, date_to, symbol, interval)


@router.get("/triangle")
async def strategy_triangle(
    date_from=None, date_to=None, symbol='ADAUSDT', interval='1d'
):
    return triangle.calc(date_from, date_to, symbol, interval)
