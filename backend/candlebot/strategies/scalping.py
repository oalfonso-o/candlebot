import math
import logging

from candlebot.strategies.base import StrategyBase
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

logger = logging.getLogger(__name__)


class StrategyScalping(StrategyBase):
    _id = 'scalping'
    variables = []
    indicators = [
        IndicatorSMMA21,
        IndicatorSMMA50,
        IndicatorSMMA200,
        IndicatorWilliamBullFractals,
        IndicatorWilliamBearFractals,
        IndicatorStochRSID,
        IndicatorStochRSIK,
    ]
    open_conditions = [
        'trend_long',
        'circular_queue_is_full',
        'crow_low_gt_smma21',
        'rsi_k_crow_lt_10',
        'rsi_k_crow_gt_rsi_d_crow',
    ]
    trend_reverse_flag = False

    def _update_direction(self, row):
        if (
            math.isnan(row['smma21'])
            or math.isnan(row['smma50'])
            or math.isnan(row['smma200'])
            or len(self.queue) != self.len_queue
        ):
            self.direction = 0
        elif (
            row['smma21'] > row['smma50'] > row['smma200']
            and all((c['smma21'] > c['smma200'] for c in self.queue))
        ):
            if self.trend_reverse_flag:
                self.direction = 1
            else:
                self.trend_reverse_flag = True
        elif (
            row['smma21'] < row['smma50'] < row['smma200']
            and all((c['smma21'] < c['smma200'] for c in self.queue))
        ):
            if self.trend_reverse_flag:
                self.direction = -1
            else:
                self.trend_reverse_flag = True
        else:
            self.direction = 0
            self.trend_reverse_flag = False

    def _must_close_long(self, row):
        if not self.last_open_pos_close_value:
            return 0
        last_open_value_pips = self.last_open_pos_close_value / self.pips_total
        high_diff = last_open_value_pips * self.win_pips_margin
        low_diff = last_open_value_pips * self.loss_pips_margin
        # standard win
        if row['high'] - self.last_open_pos_close_value > high_diff:
            close_pos = self.last_open_pos_close_value + high_diff
            self.wallet.stats.wins += 1
            logging.info(
                f'wins {self.wallet.stats.wins} - '
                f'loses {self.wallet.stats.losses}'
            )
            return close_pos
        # standard lose
        elif self.last_open_pos_close_value - row['low'] > low_diff:
            close_pos = self.last_open_pos_close_value - low_diff
            self.wallet.stats.losses += 1
            logging.info(
                f'wins {self.wallet.stats.wins} - '
                f'loses {self.wallet.stats.losses}'
            )
            return close_pos
        return 0
