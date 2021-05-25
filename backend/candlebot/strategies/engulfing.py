import logging
from typing import Tuple

import pandas as pd

from candlebot import utils
from candlebot.indicators.engulfing import IndicatorEngulfing
from candlebot.models.wallet import Wallet

logger = logging.getLogger(__name__)


class StrategyEngulfing:
    _id = 'engulfing'
    indicators = [IndicatorEngulfing]
    variables = []

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.wallet = Wallet()
        self.last_open_candle = 0
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        direction = 0
        for i, row in self.df.iterrows():
            if self._must_open_long(row, direction):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.open_pos('long', row['close'], timestamp)
                self.last_open_candle = row['open']
                direction = 1
            elif self._must_close_long(row, direction):
                close = row['close']
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                if row['close'] < self.last_open_candle:
                    close = self.last_open_candle
                self.wallet.close_pos('long', close, timestamp)
                direction = -1
        return self.df, self.wallet

    def _must_open_long(self, row, direction):
        if (
            (not direction or direction == -1)
            and row['engulfing'] == 100
        ):
            return True
        return False

    def _must_close_long(self, row, direction):
        if (
            (not direction or direction == 1)
            and (
                row['engulfing'] == -100
                or row['close'] < self.last_open_candle
            )
        ):
            return True
        return False
