from fastapi import APIRouter

from candlebot.api.strategies import generic

router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def calculate_strategy(
    strategy, date_from=None, date_to=None, symbol='ADAUSDT', interval='1d',
):
    return generic.calc(strategy, date_from, date_to, symbol, interval)
