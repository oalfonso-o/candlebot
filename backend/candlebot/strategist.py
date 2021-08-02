import logging
import pandas as pd

from candlebot.strategies.ema import StrategyEMA
from candlebot.strategies.engulfing import StrategyEngulfing
from candlebot.strategies.triangle import StrategyTriangle
from candlebot.strategies.scalping import StrategyScalping
from candlebot.strategies.scalping_ema_10_20 import StrategyScalpingEMA10_20
from candlebot.strategies.scalping_yolo import StrategyScalpingYolo
from candlebot import utils
from candlebot import constants

logger = logging.getLogger(__name__)


class Strategist:

    strategies = {
        'ema': StrategyEMA,
        'engulfing': StrategyEngulfing,
        'triangle': StrategyTriangle,
        'scalping': StrategyScalping,
        'scalping_ema_10_20': StrategyScalpingEMA10_20,
        'scalping_yolo': StrategyScalpingYolo,
    }

    @classmethod
    def calc(cls, candles: list, strategy: str) -> pd.DataFrame:
        candles_df = pd.DataFrame(candles)
        for field in constants.KLINE_FIELDS:
            candles_df[field] = candles_df[field].apply(float)
        candles_df['_id'] = candles_df['_id'].apply(
            lambda _id: utils.timestamp_to_date(_id)
        )
        strat_df, wallet = cls.strategies[strategy](candles_df).calc()
        return strat_df, wallet
