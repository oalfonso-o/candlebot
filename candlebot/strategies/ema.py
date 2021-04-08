import logging
from typing import Tuple

import pandas as pd

from candlebot import settings
from candlebot import utils
from candlebot.indicators.ema import IndicatorEMA
from candlebot.models.wallet import Wallet

logger = logging.getLogger(__name__)


class StrategyEMA:
    indicators = [IndicatorEMA]

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.drop_factor = settings.BT['strategies']['ema']['drop_factor']
        self.wallet = Wallet()
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        lowest = None
        highest = None
        direction = 0
        for i, row in self.df.iterrows():
            if lowest is None and highest is None:
                lowest = row
                highest = row
                continue
            if self._must_buy(row, lowest, direction):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.open_pos('long', row['close'], timestamp)
                direction = 1
            elif self._must_sell(row, highest, direction):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.close_pos('long', row['close'], timestamp)
                direction = -1
            if (row['trend_ema_fast'] - highest['trend_ema_fast']) > 0:
                highest = row
            if (row['trend_ema_fast'] - lowest['trend_ema_fast']) < 0:
                lowest = row
        return self.df, self.wallet.chart_data()

    def _must_buy(self, row, lowest, direction):
        return bool(
            (row['trend_ema_fast'] - lowest['trend_ema_fast'])
            > (lowest['trend_ema_fast'] * self.drop_factor)
            and (not direction or direction < 0)
        )

    def _must_sell(self, row, highest, direction):
        return bool(
            (highest['trend_ema_fast'] - row['trend_ema_fast'])
            > (highest['trend_ema_fast'] * self.drop_factor)
            and (not direction or direction > 0)
        )
