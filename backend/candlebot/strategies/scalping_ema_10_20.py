import logging
import math
import pandas as pd

from candlebot.indicators.ema import (
    IndicatorEMA10,
    IndicatorEMA20,
)
from candlebot.strategies.base import StrategyBase

logger = logging.getLogger(__name__)


class StrategyScalpingEMA10_20(StrategyBase):
    _id = 'scalping_ema_10_20'
    variables = []
    open_conditions = [
        'trend_long',
        'circular_queue_is_full',
    ]
    custom_indicators = [
        IndicatorEMA10,
        IndicatorEMA20,
    ]

    def __init__(self, df: pd.DataFrame):
        self.indicators = self.custom_indicators
        super().__init__(df)

    def _update_direction(self, row):
        if (
            math.isnan(row['ema10'])
            or math.isnan(row['ema20'])
            or not self.circular_queue_is_full(row)
        ):
            self.direction = 0
        elif row['ema10'] > row['ema20']:
            self.direction = 1
        elif row['ema10'] < row['ema20']:
            self.direction = -1
        else:
            self.direction = 0

    def _must_open_long(self, row):
        if (
            not self.last_open_pos_close_value
            and all([getattr(self, f)(row) for f in self.open_conditions])
        ):
            return True
        return False

    def _must_close_long(self, row):
        if not self.last_open_pos_close_value:
            return 0
        last_open_value_pips = self.last_open_pos_close_value / self.pips_total
        high_diff = last_open_value_pips * self.win_pips_margin
        low_diff = last_open_value_pips * self.loss_pips_margin
        # standard win
        if row['high'] - self.last_open_pos_close_value > high_diff:
            close_pos = self.last_open_pos_close_value + high_diff
            self.wins += 1 * self.count_open_pos
            logging.info(f'wins {self.wins} - loses {self.losses}')
            return close_pos
        # standard lose
        elif self.last_open_pos_close_value - row['low'] > low_diff:
            close_pos = self.last_open_pos_close_value - low_diff
            self.losses += 1
            logging.info(f'wins {self.wins} - loses {self.losses}')
            return close_pos
        return 0
