import logging
from typing import Tuple

import pandas as pd

from candlebot import utils
from candlebot.settings import Settings
from candlebot.indicators.ema import IndicatorEMA
from candlebot.models.wallet import Wallet

logger = logging.getLogger(__name__)


class StrategyEMA:
    _id = 'ema'
    indicators = [IndicatorEMA]
    variables = [
        {'name': 'drop_factor', 'type': 'num'},
    ]

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.drop_factor = Settings.BT['strategies']['ema']['drop_factor']
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
            if self._must_open_long_close_short(row, lowest, direction):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.open_pos('long', row['close'], timestamp)
                # self.wallet.close_pos('short', row['close'], timestamp)
                direction = 1
                highest = row
            elif self._must_close_long_open_short(row, highest, direction):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.close_pos('long', row['close'], timestamp)
                # self.wallet.open_pos('short', row['close'], timestamp)
                direction = -1
                lowest = row
            if (row['ema'] - highest['ema']) > 0:
                highest = row
            if (row['ema'] - lowest['ema']) < 0:
                lowest = row
        return self.df, self.wallet

    def _must_open_long_close_short(self, row, lowest, direction):
        return bool(
            (row['ema'] - lowest['ema'])
            > (lowest['ema'] * self.drop_factor)
            and (not direction or direction < 0)
        )

    def _must_close_long_open_short(self, row, highest, direction):
        return bool(
            (highest['ema'] - row['ema'])
            > (highest['ema'] * self.drop_factor)
            and (not direction or direction > 0)
        )
