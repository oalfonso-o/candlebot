from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, TypedDict, Optional

from candlebot import constants
from candlebot import utils
from candlebot.db import db_find
from candlebot.backtesting import Backtesting
from candlebot.strategist import Strategist


router = APIRouter(
    prefix="/backtesting",
    tags=["backtesting"],
    responses={404: {"description": "Not found"}},
)


class BacktestListKwargs(TypedDict):
    test_id: Optional[str] = ''
    strategy: Optional[str] = ''
    symbol: Optional[str] = ''
    interval: Optional[str] = ''
    sort_field: Optional[str] = 'profit_percentage'
    sort_direction: Optional[int] = -1
    test_date_from: Optional[str] = ''
    test_date_to: Optional[str] = ''
    limit: Optional[int] = 15


backtest_list_kwargs = BacktestListKwargs()


@router.get("/list")
async def backtest_list(**backtest_list_kwargs):
    date_from_without_dash = backtest_list_kwargs.date_from.replace('-', '')
    date_to_without_dash = backtest_list_kwargs.date_to.replace('-', '')
    date_from = utils.str_to_date(date_from_without_dash)
    date_to = utils.str_to_date(date_to_without_dash)
    backtest_list_kwargs['test_date_from'] = date_from
    backtest_list_kwargs['test_date_to'] = date_to
    last_backtests = db_find.find_last_backtests()
    best_backtests = db_find.find_best_backtests()
    filtered_backtests = db_find.find_filtered_backtests(
        **backtest_list_kwargs)
    return {
        'last_backtests': last_backtests,
        'best_backtests': best_backtests,
        'filtered_backtests': filtered_backtests,
    }


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
