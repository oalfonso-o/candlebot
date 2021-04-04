import logging
import datetime

from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from crypto.db import db_find
from crypto import constants

logger = logging.getLogger(__name__)


class Charter:

    @classmethod
    def show_charts(
        cls, symbol, interval, date_from=None, date_to=None, show_plot=True
    ):
        logger.info(f'Trading {symbol}')
        query = {}
        if date_from or date_to:
            query = {'_id': {}}
            if date_from:
                query['_id']['$gte'] = int(date_from)
            if date_to:
                query['_id']['$lte'] = int(date_to)
        all_cursor = db_find.find(
            symbol, interval, query, constants.KLINE_FIELDS)
        df = pd.DataFrame(list(all_cursor))
        df['_id'] = df['_id'].apply(
            lambda _id: datetime.datetime.fromtimestamp(_id / 1000)
        )
        df['ema'] = df['close'].ewm(
            span=constants.CONFIG_EMA_WINDOW,
            adjust=constants.CONFIG_EMA_ADJUST,
        ).mean()
        operations = cls._calc_buy_sell(df)
        if show_plot:
            candlestick = go.Candlestick(
                x=df['_id'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=symbol,
            )
            ema_scatter = go.Scatter(
                x=df['_id'],
                y=df['ema'],
                name='EMA',
                yaxis='y2',
            )
            buy_sell_scatter = go.Scatter(
                x=df['_id'],
                y=df['bs'],
                name='buy/sell',
                yaxis='y2',
                mode='markers',
                marker=dict(color='crimson', size=7),
            )
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(candlestick)
            fig.add_trace(ema_scatter, secondary_y=True)
            fig.add_trace(buy_sell_scatter, secondary_y=True)
            fig['layout'].update(title='EMA Chart', xaxis=dict(tickangle=-90))
            plot(fig)
        return operations

    @classmethod
    def _calc_buy_sell(cls, df):
        lowest = None
        highest = None
        df['bs'] = np.NaN
        last_buy = 0
        last_sell = 0
        direction = 0
        operations = {
            'buys': 0,
            'sells': 0,
            'long_profit': 0,
            'short_profit': 0,
        }
        for i, row in df.iterrows():
            row['close'] = float(row['close'])
            row['ema'] = float(row['ema'])
            row['bs'] = float(0)
            if lowest is None and highest is None:
                lowest = row
                highest = row
                continue
            if cls._must_buy(row, lowest, direction):
                df.at[i, 'bs'] = row['close']
                operations['buys'] += 1
                last_buy = row['close']
                if last_sell:
                    operations['short_profit'] += last_sell - row['close']
                direction = 1
            elif cls._must_sell(row, highest, direction):
                df.at[i, 'bs'] = row['close']
                operations['sells'] += 1
                last_sell = row['close']
                if last_buy:
                    operations['long_profit'] += row['close'] - last_buy
                direction = -1
            if (row['ema'] - highest['ema']) > 0:
                highest = row
            if (row['ema'] - lowest['ema']) < 0:
                lowest = row
        return operations

    @staticmethod
    def _must_buy(row, lowest, direction):
        return bool(
            (row['ema'] - lowest['ema'])
            > (lowest['ema'] * constants.CONFIG_EMA_DROP_PERCENT)
            and (not direction or direction < 0)
        )

    @staticmethod
    def _must_sell(row, highest, direction):
        return bool(
            (highest['ema'] - row['ema'])
            > (highest['ema'] * constants.CONFIG_EMA_DROP_PERCENT)
            and (not direction or direction > 0)
        )
