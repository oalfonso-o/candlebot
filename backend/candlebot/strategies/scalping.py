import logging
from typing import Tuple

import pandas as pd

from candlebot import utils
from candlebot.indicators.engulfing import IndicatorEngulfing
from candlebot.models.wallet import Wallet
from candlebot.utils.circular_queue import CircularQueue

logger = logging.getLogger(__name__)

BULL_HAMMER = 'bull_hammer'
BEAR_HAMMER = 'bear_hammer'
DOJI = 'doji'
START_BULL_ENGULFING = 'start_bull_engulfing'
FULL_BULL_ENGULFING = 'full_bull_engulfing'
START_BEAR_ENGULFING = 'start_bear_engulfing'
FULL_BEAR_ENGULFING = 'full_bear_engulfing'

ENGULFING_MIN_DIFF_PIPS = 2


class StrategyScalping:
    _id = 'scalping'
    indicators = [IndicatorEngulfing]
    variables = []

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.wallet = Wallet()
        self.past_candles = CircularQueue(5)
        self.last_open_pos_close_value = 0
        self.pips_total = 10000
        self.win_pips_margin = 20
        self.loss_pips_margin = 40
        self.wins = 0
        self.losses = 0
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        for i, row in self.df.iterrows():
            self._tag_candles(row)
            if self._must_open_long(row):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.open_pos('long', row['close'], timestamp)
                self.last_open_pos_close_value = row['close']
            else:
                close_pos = self._must_close_long(row)
                if close_pos:
                    timestamp = utils.datetime_to_timestamp(
                        row['_id'].to_pydatetime()
                    )
                    self.last_open_pos_close_value = 0
                    self.wallet.close_pos('long', close_pos, timestamp)
        print(f'wins: {self.wins}')
        print(f'losses: {self.losses}')
        return self.df, self.wallet

    def _tag_candles(self, row):
        tags = []
        queue = self.past_candles.get_queue()
        prev_row = queue[0]
        body = row['open'] - row['close']
        is_red_candle = body > 0
        is_green_candle = body < 0
        body = abs(body)
        if not body:
            color = 'green'  # dummy color for first dogi
            if isinstance(prev_row, pd.core.series.Series):
                color = prev_row['color']
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
                isinstance(prev_row, pd.core.series.Series)
                and prev_row['color'] == 'red'
            ):
                prev_body = prev_row['open'] - prev_row['close']
                diff_body = body - prev_body
                pip_value = row['close'] / self.pips_total
                if diff_body > pip_value * ENGULFING_MIN_DIFF_PIPS:
                    tags.append(FULL_BULL_ENGULFING)

        row['tags'] = tags
        self.past_candles.enqueue(row)

    def _must_open_long(self, row):
        if FULL_BULL_ENGULFING in row['tags']:
            return True
        return False

    def _must_close_long(self, row):
        if not self.last_open_pos_close_value:
            return 0
        last_open_value_pips = self.last_open_pos_close_value / self.pips_total
        high_diff = last_open_value_pips * self.win_pips_margin
        low_diff = last_open_value_pips * self.loss_pips_margin
        if abs(self.last_open_pos_close_value - row['high']) > high_diff:
            close_pos = self.last_open_pos_close_value + high_diff
            self.wins += 1
            return close_pos
        if abs(self.last_open_pos_close_value - row['low']) > low_diff:
            close_pos = self.last_open_pos_close_value - low_diff
            self.losses += 1
            return close_pos
        return 0
