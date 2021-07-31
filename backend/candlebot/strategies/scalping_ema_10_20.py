import logging
import math
import pandas as pd

from candlebot.indicators.ema import (
    IndicatorEMA10,
    IndicatorEMA20,
)
from candlebot.indicators.zigzag import IndicatorZigZag
from candlebot.strategies.base import StrategyBase

logger = logging.getLogger(__name__)


class StrategyScalpingEMA10_20(StrategyBase):
    _id = 'scalping_ema_10_20'
    variables = []
    open_conditions = [
        'trend_long',
        'circular_queue_is_full',
        'ago_2_open_gt_ema10',
        'ago_2_close_lt_ema10',
        'ago_2_color_red',
        'ago_1_high_lt_ema10',
        'crow_color_green',
        'crow_close_gt_ema10',
    ]
    custom_indicators = [
        IndicatorEMA10,
        IndicatorEMA20,
        IndicatorEMA20,
        IndicatorZigZag,
    ]
    close_win_conditions = [
        'ema10_lt_ema20',
        'crow_low_gt_open_pos',
    ]
    close_lose_conditions = [
        'reached_stop_loss',
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
        if not self.last_open_pos_close_value:
            for f in self.open_conditions:
                if not getattr(self, f)(row):
                    return False  # lazy loading all open_conditions
                self.stop_loss = row['close'] - 20  # TODO: REMOVE THIS SHIT, CALCULATE STOP LOSS WITH ZIGZAG
            return True
        return False

    def _must_close_long(self, row):
        if not self.last_open_pos_close_value:
            return 0
        if all([getattr(self, f)(row) for f in self.close_win_conditions]):
            return self._custom_close(row, 'ema10 under ema20')
        elif all([getattr(self, f)(row) for f in self.close_lose_conditions]):
            self.stop_loss = 0
            return self._custom_close(row, 'stoploss')
        return 0
