from fastapi import APIRouter

from candlebot.api.strategies import ema

router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
    responses={404: {"description": "Not found"}},
)


@router.get("/ema")
async def strategy_ema(
    date_from=None, date_to=None, symbol='ADAEUR', interval='1d'
):
    return ema.calc(date_from, date_to, symbol, interval)
