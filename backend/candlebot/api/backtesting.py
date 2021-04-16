from fastapi import APIRouter
from pydantic import BaseModel

from candlebot import utils
from candlebot.backtesting import Backtesting


router = APIRouter(
    prefix="/backtesting",
    tags=["backtesting"],
    responses={404: {"description": "Not found"}},
)


class BacktestBody(BaseModel):
    date_from: str
    date_to: str
    symbols: str
    intervals: str
    strategy: str


@router.post("/")
async def backtest_create(body: BacktestBody):
    date_from_without_dash = body.date_from.replace('-', '')
    date_from = utils.date_to_timestamp(date_from_without_dash)
    date_to_without_dash = body.date_to.replace('-', '')
    date_to = utils.date_to_timestamp(date_to_without_dash)
    bt = Backtesting(
        date_from,
        date_to,
        body.symbols,
        body.intervals,
        body.strategy,
    )
    response = bt.test()
    return response
