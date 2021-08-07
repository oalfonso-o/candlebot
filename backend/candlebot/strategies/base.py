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
    markers_indicators = []
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
    post_close_actions = [
        'remove_stop_loss',
        'remove_last_open_pos_close_value',
    ]
    len_queue = 15
    stop_loss = 0
    pips_total = 10000
    win_pips_margin = 20
    loss_pips_margin = 20

    def __init__(self, df: pd.DataFrame):
        self.df = df
        for indicator in self.indicators + self.markers_indicators:
            self.df = indicator.apply(self.df)
        self.df_ready_conditions += self.custom_df_ready_conditions
        self.wallet = Wallet()
        self.past_candles = CircularQueue(self.len_queue)
        self.last_open_pos_close_value = 0
        self.direction = 0
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
            else:
                close_pos = self._must_close_long(row)
                if close_pos:
                    timestamp = utils.datetime_to_timestamp(
                        row['_id'].to_pydatetime()
                    )
                    self.wallet.close_pos('long', close_pos, timestamp)
                    self._post_close_actions(row)
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
        if not self.last_open_pos_close_value:  # this only allows 1 open
            for f in self.open_conditions:
                if type(f) == str:
                    if not getattr(self, f)(row):
                        return False
                elif type(f) == list:  # multiple AND conditions in an OR list of conditions: [[1 and 2 and 3] or [4 and 5 and 6]]  # noqa
                    one_OR_condition_met = False
                    for or_conditions in f:
                        if all([
                            getattr(self, f2)(row)
                            for f2 in or_conditions
                        ]):
                            one_OR_condition_met = True
                            break
                    if not one_OR_condition_met:
                        return False
                else:
                    raise Exception('Unsupported type of open long')
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

    def _post_close_actions(self, row):
        for f in self.post_close_actions:
            getattr(self, f)(row)
