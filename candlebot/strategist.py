import logging
import pandas as pd

from candlebot.strategies.ema import StrategyEMA
from candlebot import utils
from candlebot import constants

logger = logging.getLogger(__name__)


class Strategist:

    strategies = {
        'ema': StrategyEMA,
    }

    @classmethod
    def calc(cls, candles: list, strategy: str) -> pd.DataFrame:
        candles_df = pd.DataFrame(candles)
        for field in constants.KLINE_FIELDS:
            candles_df[field] = candles_df[field].apply(float)
        candles_df['_id'] = candles_df['_id'].apply(
            lambda _id: utils.timestamp_to_date(_id)
        )
        strat_df, stats = cls.strategies[strategy](candles_df).calc()
        return strat_df, stats