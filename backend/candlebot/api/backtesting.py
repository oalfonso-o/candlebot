from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from candlebot import utils
from candlebot import constants
from candlebot.db import db_find
from candlebot.backtesting import Backtesting
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
    strategies = {}
    for s_id, Strategy in Strategist.strategies.items():
        s_variables = []
        indicators = {}
        for v in Strategy.variables:
            v['id'] = constants.BACKTESTING_STRAT_IND_SEPARATOR.join([
                constants.BACKTESTING_STRAT_PREFIX, Strategy._id, v['name']
            ])
            s_variables.append(v)
        for Indicator in Strategy.indicators:
            i_variables = []
            for v in Indicator.variables:
                v['id'] = constants.BACKTESTING_STRAT_IND_SEPARATOR.join([
                    constants.BACKTESTING_IND_PREFIX, Indicator._id, v['name']
                ])
                i_variables.append(v)
            indicators[Indicator._id] = i_variables
        strategies[s_id] = {
            'variables': s_variables,
            'indicators': indicators,
        }
    return strategies


class BacktestArgs(BaseModel):
    date_from: str
    date_to: str
    strategy: str
    symbols: List[str]
    intervals: List[str]
    strategy_fields: List[dict]
    indicators_fields: List[dict]


@router.post("/create")
async def backtest_create(args: BacktestArgs):
    bt = Backtesting()
    bt.test_from_web(args)
    return {}
