import datetime
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
from candlebot.models.wallet import Wallet
from candlebot.utils.circular_queue import CircularQueue

logger = logging.getLogger(__name__)

BULL_HAMMER = 'bull_hammer'
BEAR_HAMMER = 'bear_hammer'
DOJI = 'doji'
FULL_BULL_ENGULFING = 'full_bull_engulfing'

ENGULFING_MIN_DIFF_PIPS = 2


class StrategyScalping:
    _id = 'scalping'
    indicators = [
        IndicatorSMMA21,
        IndicatorSMMA50,
        IndicatorSMMA200,
        IndicatorWilliamBullFractals,
        IndicatorWilliamBearFractals,
    ]
    variables = [
        {'name': 'drop_factor', 'type': 'num'},
    ]

    def __init__(self, df: pd.DataFrame):
        self.df = df
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)
        self.wallet = Wallet()
        self.past_candles = CircularQueue(5)
        self.last_open_pos_close_value = 0
        self.pips_total = 10000
        self.win_pips_margin = 20
        self.loss_pips_margin = 50
        self.wins = 0
        self.losses = 0
        self.count_open_pos = 0
        self.prev_row = None
        self.direction = 0
        self.diff_ema_trend_pips = 5
        self.trend_reverse_flag = False
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)
        self.df['engulfing'] = False

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        for i, row in self.df.iterrows():
            # TODO: remove dirty testing hardcoded filter
            day_to_test = datetime.datetime(year=2021, month=7, day=10)
            if row['_id'] < day_to_test:
                continue
            queue = self.past_candles.get_queue()
            self.prev_row = queue[0]
            self._tag_candles(row, i)
            self._update_direction(row)
            if self._must_open_long(row, queue):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.open_pos('long', row['close'], timestamp)
                self.last_open_pos_close_value = row['close']
                self.count_open_pos += 1
            else:
                close_pos = self._must_close_long(row, queue)
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
        logger.info(f'balance % earn: {self.wallet.balance_origin / self.wallet.balance_origin_start * 100}')  # noqa
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
            tags.append(DOJI)
        elif is_red_candle:
            row['color'] = 'red'
            # tag bull hammer
            low_wick = row['close'] - row['low']
            if low_wick / 3 > body:
                tags.append(BULL_HAMMER)

        elif is_green_candle:
            row['color'] = 'green'
            # tag bear hammer
            high_wick = row['high'] - row['close']
            if high_wick / 3 > body:
                tags.append(BEAR_HAMMER)
            # tag bull engulfing
            if (
                isinstance(self.prev_row, pd.core.series.Series)
                and self.prev_row['color'] == 'red'
            ):
                prev_body = self.prev_row['open'] - self.prev_row['close']
                diff_body = body - prev_body
                pip_value = row['close'] / self.pips_total
                if diff_body > pip_value * ENGULFING_MIN_DIFF_PIPS:
                    tags.append(FULL_BULL_ENGULFING)
                    self.df.loc[index, 'engulfing'] = True

        row['tags'] = tags
        self.past_candles.enqueue(row)

    def _update_direction(self, row):
        if (
            math.isnan(row['smma21'])
            or math.isnan(row['smma50'])
            or math.isnan(row['smma200'])
        ):
            self.direction = 0
        elif row['smma21'] > row['smma50'] > row['smma200']:
            if self.trend_reverse_flag:
                self.direction = 1
            else:
                self.trend_reverse_flag = True
        elif row['smma21'] < row['smma50'] < row['smma200']:
            if self.trend_reverse_flag:
                self.direction = -1
            else:
                self.trend_reverse_flag = True
        else:
            self.direction = 0
            self.trend_reverse_flag = False

    def _must_open_long(self, row, queue):
        two_candles_ago = queue[1] if len(queue) == 5 else None
        if two_candles_ago is None:
            return False
        if (
            # FULL_BULL_ENGULFING in row['tags']
            two_candles_ago['william_bull_fractals']
            and (
                row['low'] > row['smma21']
                and two_candles_ago['low'] > row['smma21']
            )
            and self.direction == 1
        ):
            return True
        return False

    def _must_close_long(self, row, queue):
        if not self.last_open_pos_close_value:
            return 0
        # two_candles_ago = queue[1] if len(queue) == 5 else None
        last_open_value_pips = self.last_open_pos_close_value / self.pips_total
        high_diff = last_open_value_pips * self.win_pips_margin
        low_diff = last_open_value_pips * self.loss_pips_margin
        # # premature close because of bear fractal
        # if (
        #     two_candles_ago is not None
        #     and self.last_open_pos_close_value
        #     and two_candles_ago['william_bear_fractals']
        # ):
        #     margin = row['close'] - self.last_open_pos_close_value
        #     if margin > 0 and margin > high_diff:
        #         self.wins += 1
        #     elif margin <= 0:
        #         self.losses += 1
        #     return row['close']
        # win
        if row['high'] - self.last_open_pos_close_value > high_diff:
            close_pos = self.last_open_pos_close_value + high_diff
            self.wins += 1 * self.count_open_pos
            return close_pos
        # lose
        elif self.last_open_pos_close_value - row['low'] > low_diff:
            close_pos = self.last_open_pos_close_value - low_diff
            self.losses += 1
            return close_pos
        return 0
