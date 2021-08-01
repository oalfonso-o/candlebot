from abc import abstractmethod
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
from candlebot.strategies.conditions import Conditions
from candlebot.strategies import constants

logger = logging.getLogger(__name__)

FEE_PERCENT = 0.16


class StrategyBase(Conditions):  # TODO: abstract class
    _id = 'must_be_overriden'  # TODO: abstract property
    indicators = [
        IndicatorSMMA21,
        IndicatorSMMA50,
        IndicatorSMMA200,
        IndicatorWilliamBullFractals,
        IndicatorWilliamBearFractals,
        IndicatorStochRSID,
        IndicatorStochRSIK,
    ]
    variables = []
    open_conditions = []
    close_conditions = []

    def __init__(self, df: pd.DataFrame):
        self.df = df
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)
        self.wallet = Wallet()
        self.len_queue = 200
        self.past_candles = CircularQueue(self.len_queue)
        self.last_open_pos_close_value = 0
        self.pips_total = 10000
        self.win_pips_margin = 20
        self.loss_pips_margin = 20
        self.wins = 0
        self.losses = 0
        self.count_open_pos = 0
        self.prev_row = None
        self.direction = 0
        self.trend_reverse_flag = False
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)
        self.df['engulfing'] = False
        self.stop_loss = 0

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        for i, row in self.df.iterrows():
            self.queue = self.past_candles.get_queue()
            self.prev_row = self.queue[0]
            self._tag_candles(row, i)
            self._update_direction(row)
            if self._must_open_long(row):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.open_pos('long', row['close'], timestamp)
                self.last_open_pos_close_value = row['close']
                self.count_open_pos += 1
            else:
                close_pos = self._must_close_long(row)
                if close_pos:
                    timestamp = utils.datetime_to_timestamp(
                        row['_id'].to_pydatetime()
                    )
                    self.last_open_pos_close_value = 0
                    self.wallet.close_pos('long', close_pos, timestamp)
                    self.count_open_pos = 0
        logger.info(f'wins: {self.wins}')
        logger.info(f'losses: {self.losses}')
        logger.info(f'win/lose: {self.wins / self.losses if self.losses else str(self.wins)+":-"}')  # noqa
        logger.info(f'final balance: {self.wallet.balance_origin}')
        open_pos = self.wallet.amount_to_open if self.last_open_pos_close_value else 0  # noqa
        logger.info(f'open position: {open_pos}')
        logger.info(f'balance % earn: {(self.wallet.balance_origin + open_pos) / self.wallet.balance_origin_start * 100}')  # noqa
        return self.df, self.wallet

    def _tag_candles(self, row, index):
        tags = []
        body = row['open'] - row['close']
        is_red_candle = body > 0
        is_green_candle = body < 0
        body = abs(body)
        if not body:
            color = 'green'  # dummy color for first dogi
            if isinstance(self.prev_row, pd.core.series.Series):
                color = self.prev_row['color']
            row['color'] = color
            tags.append(constants.DOJI)
        elif is_red_candle:
            row['color'] = 'red'
            # tag bull hammer
            low_wick = row['close'] - row['low']
            if low_wick / 3 > body:
                tags.append(constants.BULL_HAMMER)

        elif is_green_candle:
            row['color'] = 'green'
            # tag bear hammer
            high_wick = row['high'] - row['close']
            if high_wick / 3 > body:
                tags.append(constants.BEAR_HAMMER)
            # tag bull engulfing
            if (
                isinstance(self.prev_row, pd.core.series.Series)
                and self.prev_row['color'] == 'red'
            ):
                prev_body = self.prev_row['open'] - self.prev_row['close']
                diff_body = body - prev_body
                pip_value = row['close'] / self.pips_total
                if diff_body > pip_value * constants.ENGULFING_MIN_DIFF_PIPS:
                    tags.append(constants.FULL_BULL_ENGULFING)
                    self.df.loc[index, 'engulfing'] = True

        row['tags'] = tags
        self.past_candles.enqueue(row)

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

    @abstractmethod
    def _must_open_long(self, row):
        ...

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

    def _custom_close(self, row, reason):
        win_desired = (
            self.last_open_pos_close_value
            + (self.last_open_pos_close_value / 100 * FEE_PERCENT)
        )
        if row['close'] < win_desired:
            self.losses += 1
            logging.info(f'LOSE close because {reason}')
            return row['close']
        elif row['close'] >= win_desired:
            self.wins += 1
            logging.info(f'WIN close because {reason}')
            return row['close']
