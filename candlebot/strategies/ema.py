import logging
from typing import Tuple

import pandas as pd
import numpy as np

from candlebot.indicators.ema import IndicatorEMA
from candlebot import settings

logger = logging.getLogger(__name__)


class StrategyEMA:
    indicators = [IndicatorEMA]

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.drop_factor = settings.BT['strategies']['ema']['drop_factor']
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        lowest = None
        highest = None
        self.df['bs'] = np.NaN
        last_buy = 0
        last_sell = 0
        direction = 0
        long_profit_percents = []
        short_profit_percents = []
        stats = {
            'buys': 0,
            'sells': 0,
            'long_profit': 0,
            'short_profit': 0,
        }
        for i, row in self.df.iterrows():
            row['bs'] = float(0)
            if lowest is None and highest is None:
                lowest = row
                highest = row
                continue
            if self._must_buy(row, lowest, direction):
                self.df.at[i, 'bs'] = row['close']
                stats['buys'] += 1
                last_buy = row['close']
                if last_sell:
                    profit = last_sell - row['close']
                    stats['short_profit'] += profit
                    percent_profit = profit / last_sell
                    short_profit_percents.append(percent_profit)
                direction = 1
            elif self._must_sell(row, highest, direction):
                self.df.at[i, 'bs'] = row['close']
                stats['sells'] += 1
                last_sell = row['close']
                if last_buy:
                    profit = row['close'] - last_buy
                    stats['long_profit'] += profit
                    percent_profit = profit / last_buy
                    long_profit_percents.append(percent_profit)
                direction = -1
            if (row['trend_ema_fast'] - highest['trend_ema_fast']) > 0:
                highest = row
            if (row['trend_ema_fast'] - lowest['trend_ema_fast']) < 0:
                lowest = row
        self._calc_avg(stats, long_profit_percents, short_profit_percents)
        return self.df, stats

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

    @staticmethod
    def _calc_avg(stats, long_profit_percents, short_profit_percents):
        if long_profit_percents:
            stats['long_profit_avg'] = (
                sum(long_profit_percents)
                / len(long_profit_percents)
            )
        if short_profit_percents:
            stats['short_profit_avg'] = (
                sum(short_profit_percents)
                / len(short_profit_percents)
            )
