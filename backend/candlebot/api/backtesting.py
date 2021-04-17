from fastapi import APIRouter
from pydantic import BaseModel

from candlebot import utils
from candlebot.backtesting import Backtesting
from candlebot.db import db_find
from candlebot.strategist import Strategist


router = APIRouter(
    prefix="/backtesting",
    tags=["backtesting"],
    responses={404: {"description": "Not found"}},
)


@router.get("/list")
async def backtest_list():
    return db_find.find_backtests()


@router.get("/strategies")
async def backtest_strategies():
    strategies = {
        s_id: {
            'variables': Strategy.variables,
            'indicators': {
                Indicator._id: Indicator.variables
                for Indicator in Strategy.indicators
            },
        }
        for s_id, Strategy in Strategist.strategies.items()
    }
    return strategies


class BacktestBody(BaseModel):
    date_from: str
    date_to: str
    symbols: str
    intervals: str
    strategy: str


@router.post("/create")
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
