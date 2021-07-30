import math
import logging
from typing import Tuple

import pandas as pd

from candlebot import utils
from candlebot.indicators.smma import (
    IndicatorSMMA21,
    IndicatorSMMA50,
    IndicatorSMMA200,
)
from candlebot.indicators.william_fractal import (
    IndicatorWilliamBullFractals,
    IndicatorWilliamBearFractals,
)
from candlebot.indicators.stochastic import (
    IndicatorStochRSID,
    IndicatorStochRSIK,
)
from candlebot.models.wallet import Wallet
from candlebot.utils.circular_queue import CircularQueue
from candlebot.strategies.base import StrategyBase

logger = logging.getLogger(__name__)

BULL_HAMMER = 'bull_hammer'
BEAR_HAMMER = 'bear_hammer'
DOJI = 'doji'
FULL_BULL_ENGULFING = 'full_bull_engulfing'

ENGULFING_MIN_DIFF_PIPS = 2


class StrategyScalping(StrategyBase):
    _id = 'scalping'
    variables = []

    def _must_open_long(self, row):
        if (
            not self.last_open_pos_close_value
            and self.trend_long(row)
            and self.circular_queue_is_full(row)
            and self.rsi_k_crow_is_0(row)
            and self.crow_low_gt_smma21(row)
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
