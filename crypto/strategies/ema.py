import logging
from typing import Tuple

import pandas as pd
import numpy as np

from crypto.indicators.ema import IndicatorEMA
from crypto import settings

logger = logging.getLogger(__name__)


class StrategyEMA:
    indicators = [IndicatorEMA]

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.drop_factor = settings.BT_CONFIG['ema']['drop_factor']
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        lowest = None
        highest = None
        self.df['bs'] = np.NaN
        last_buy = 0
        last_sell = 0
        direction = 0
        operations = {
            'buys': 0,
            'sells': 0,
            'long_profit': 0,
            'short_profit': 0,
            'long_profit_percents': [],
            'short_profit_percents': [],
        }
        for i, row in self.df.iterrows():
            row['close'] = float(row['close'])
            row['ema'] = float(row['ema'])
            row['bs'] = float(0)
            if lowest is None and highest is None:
                lowest = row
                highest = row
                continue
            if self._must_buy(row, lowest, direction):
                self.df.at[i, 'bs'] = row['close']
                operations['buys'] += 1
                last_buy = row['close']
                if last_sell:
                    profit = last_sell - row['close']
                    operations['short_profit'] += profit
                    percent_profit = profit / last_sell
                    operations['short_profit_percents'].append(percent_profit)
                direction = 1
            elif self._must_sell(row, highest, direction):
                self.df.at[i, 'bs'] = row['close']
                operations['sells'] += 1
                last_sell = row['close']
                if last_buy:
                    profit = row['close'] - last_buy
                    operations['long_profit'] += profit
                    percent_profit = profit / last_buy
                    operations['long_profit_percents'].append(percent_profit)
                direction = -1
            if (row['ema'] - highest['ema']) > 0:
                highest = row
            if (row['ema'] - lowest['ema']) < 0:
                lowest = row
        return self.df, operations

    def _must_buy(self, row, lowest, direction):
        return bool(
            (row['ema'] - lowest['ema'])
            > (lowest['ema'] * self.drop_factor)
            and (not direction or direction < 0)
        )

    def _must_sell(self, row, highest, direction):
        return bool(
            (highest['ema'] - row['ema'])
            > (highest['ema'] * self.drop_factor)
            and (not direction or direction > 0)
        )
