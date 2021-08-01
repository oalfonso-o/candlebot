import logging
from typing import Tuple

import pandas as pd

from candlebot import utils
from candlebot.models.wallet import Wallet
from candlebot.utils.circular_queue import CircularQueue
from candlebot.strategies.conditions import Conditions
from candlebot.strategies.closings import Closings
from candlebot.strategies.actions import PostOpenActions
from candlebot.strategies import constants

logger = logging.getLogger(__name__)


# TODO: abstract class
class StrategyBase(Conditions, Closings, PostOpenActions):
    _id = 'must_be_overriden'  # TODO: abstract property
    indicators = []
    variables = []
    df_ready_conditions = [
        'circular_queue_is_full',
    ]
    custom_df_ready_conditions = []
    direction_conditions = {
        'long': [],
        'short': [],
        'consolidation': [],
    }
    open_conditions = []
    post_open_actions = []
    close_win_conditions = []
    close_lose_conditions = []
    len_queue = 15

    def __init__(self, df: pd.DataFrame):
        self.df = df
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)
        self.df_ready_conditions += self.custom_df_ready_conditions
        self.wallet = Wallet()
        self.past_candles = CircularQueue(self.len_queue)
        self.last_open_pos_close_value = 0
        self.pips_total = 10000
        self.win_pips_margin = 20
        self.loss_pips_margin = 20
        self.wins = 0
        self.losses = 0
        self.count_open_pos = 0
        self.direction = 0
        self.trend_reverse_flag = False
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)
        self.df['engulfing'] = False
        self.stop_loss = 0

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        for i, row in self.df.iterrows():
            self.queue = self.past_candles.get_queue()
            self._tag_candles(row, i)
            if not self._df_ready(row):
                continue
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
            if isinstance(self.queue[0], pd.core.series.Series):
                color = self.queue[0]['color']
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
                isinstance(self.queue[0], pd.core.series.Series)
                and self.queue[0]['color'] == 'red'
            ):
                prev_body = self.queue[0]['open'] - self.queue[0]['close']
                diff_body = body - prev_body
                pip_value = row['close'] / self.pips_total
                if diff_body > pip_value * constants.ENGULFING_MIN_DIFF_PIPS:
                    tags.append(constants.FULL_BULL_ENGULFING)
                    self.df.loc[index, 'engulfing'] = True
        row['tags'] = tags
        self.past_candles.enqueue(row)

    def _df_ready(self, row):
        for f in self.df_ready_conditions:
            if not getattr(self, f)(row):
                return False
        return True

    def _update_direction(self, row):
        self.direction = 0
        if all([
            getattr(self, f)(row)
            for f in self.direction_conditions['long']
        ]):
            self.direction = 1
        if all([
            getattr(self, f)(row)
            for f in self.direction_conditions['short']
        ]):
            if self.direction:
                raise Exception(
                    'Direction conditions overlap between long and short')
            self.direction = -1
        if (
            self.direction_conditions['consolidation']
            and all([
                getattr(self, f)(row)
                for f in self.direction_conditions['consolidation']
            ])
        ):
            if self.direction:
                raise Exception(
                    'Direction conditions overlap between long/short and '
                    'consolidation'
                )
            self.direction = 0

    def _must_open_long(self, row):
        if not self.last_open_pos_close_value:
            for f in self.open_conditions:
                if not getattr(self, f)(row):
                    return False
            for f in self.post_open_actions:
                getattr(self, f)(row)
            return True
        return False

    def _must_close_long(self, row):
        if not self.last_open_pos_close_value:
            return 0
        close_conditions = (
            self.close_win_conditions
            + self.close_lose_conditions
        )
        for condition, close in close_conditions:
            if getattr(self, condition)(row):
                return getattr(self, close)(row, condition)
        return 0
