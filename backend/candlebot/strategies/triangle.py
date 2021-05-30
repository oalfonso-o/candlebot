import logging
from typing import Tuple

import pandas as pd

from candlebot import utils
from candlebot.indicators.triangle import (
    IndicatorMA200,
    IndicatorMA50,
    IndicatorMA20,
)
from candlebot.models.wallet import Wallet

logger = logging.getLogger(__name__)


class StrategyTriangle:
    _id = 'triangle'
    indicators = [IndicatorMA200, IndicatorMA50, IndicatorMA20]
    variables = []

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.wallet = Wallet()
        self.last_open_candle = 0
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        highs = {}
        lows = {}
        direction = 0
        for i, row in self.df.iterrows():
            row_datetime = row['_id'].to_pydatetime()
            current_day = utils.date_to_str_date(row_datetime.date())
            if current_day not in highs or current_day not in lows:
                highs[current_day] = {
                    '_id': row['_id'], 'day_highest': row['high']}
                lows[current_day] = {
                    '_id': row['_id'], 'day_lowest': row['low']}
            else:
                if highs[current_day]['day_highest'] < row['high']:
                    highs[current_day] = {
                        '_id': row['_id'], 'day_highest': row['high']}
                if lows[current_day]['day_lowest'] > row['low']:
                    lows[current_day] = {
                        '_id': row['_id'], 'day_lowest': row['low']}
            if self._must_open_long(row, direction):
                timestamp = utils.datetime_to_timestamp(
                    row_datetime
                )
                self.wallet.open_pos('long', row['close'], timestamp)
                self.last_open_candle = row['open']
                direction = 1
            elif self._must_close_long(row, direction):
                close = row['close']
                timestamp = utils.datetime_to_timestamp(
                    row_datetime
                )
                if row['close'] < self.last_open_candle:
                    close = self.last_open_candle
                self.wallet.close_pos('long', close, timestamp)
                direction = -1
        highs_list = [
            {'_id': d['_id'], 'day_highest': d['day_highest']}
            for d in highs.values()
        ]
        df_highs = pd.DataFrame(highs_list)
        lows_list = [
            {'_id': d['_id'], 'day_lowest': d['day_lowest']}
            for d in lows.values()
        ]
        df_lows = pd.DataFrame(lows_list)
        self.df = pd.merge(
            self.df,
            df_highs,
            how="left",
            on='_id',
        )
        self.df = pd.merge(
            self.df,
            df_lows,
            how="left",
            on='_id',
        )
        return self.df, self.wallet

    def _must_open_long(self, row, direction):
        return False

    def _must_close_long(self, row, direction):
        return False
