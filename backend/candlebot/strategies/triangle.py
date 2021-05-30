import logging
import datetime
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
    BACK_CHECK_POSITIONS = 4

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.wallet = Wallet()
        self.last_open_candle = 0
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        highs = {}
        lows = {}
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
        highs_list = [
            {'_id': d['_id'], 'day_highest': d['day_highest']}
            for d in highs.values()
        ]
        lows_list = [
            {'_id': d['_id'], 'day_lowest': d['day_lowest']}
            for d in lows.values()
        ]
        self._draw_triangle_in_df(highs_list, lows_list)
        self._draw_triangle_continuation_projection(highs_list, lows_list)
        return self.df, self.wallet

    def _draw_triangle_in_df(self, highs, lows):
        highs = self.remove_lower_highs(highs)
        lows = self.remove_higher_lows(lows)
        df_highs = pd.DataFrame(highs)
        df_lows = pd.DataFrame(lows)
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

    @staticmethod
    def remove_lower_highs(highs):
        while True:
            high_removed = False
            # make a copy to remove highs from original while iterating
            for i, high in enumerate(list(highs)):
                if i == 0 or i == len(highs) - 1:
                    continue
                else:
                    if (
                        high['day_highest'] < highs[i-1]['day_highest']
                        and high['day_highest'] < highs[i+1]['day_highest']
                    ):
                        highs.remove(high)
                        high_removed = True
            if not high_removed:
                break
        return highs

    @staticmethod
    def remove_higher_lows(lows):
        while True:
            low_removed = False
            # make a copy to remove lows from original while iterating
            for i, low in enumerate(list(lows)):
                if i == 0 or i == len(lows) - 1:
                    continue
                else:
                    if (
                        low['day_lowest'] > lows[i-1]['day_lowest']
                        and low['day_lowest'] > lows[i+1]['day_lowest']
                    ):
                        lows.remove(low)
                        low_removed = True
            if not low_removed:
                break
        return lows

    def _draw_triangle_continuation_projection(self, highs, lows):
        '''Check last highs and lows and project a possible triangle continuation
        '''
        last_highs = highs[-self.BACK_CHECK_POSITIONS-1:]
        last_highs.reverse()
        last_high = last_highs[0]
        for i, h in enumerate(last_highs[1:], 1):
            high_projections = []
            day_from = h['_id']
            last_high_datetime = last_high['_id'].to_pydatetime()
            diff_days = (last_high_datetime - day_from).days
            day_to = (
                last_high_datetime
                + datetime.timedelta(days=diff_days)
            )
            high_projection_from = h['day_highest']
            high_projection_to = (
                last_high['day_highest']
                - (h['day_highest'] - last_high['day_highest'])
            )
            project_from = {
                '_id': day_from, f'high_projection_{i}': high_projection_from}
            project_to = {
                '_id': day_to, f'high_projection_{i}': high_projection_to}
            high_projections.append(project_from)
            high_projections.append(project_to)
            df_highs = pd.DataFrame(high_projections)
            self.df = pd.merge(
                self.df,
                df_highs,
                how="outer",
                on='_id',
            )
