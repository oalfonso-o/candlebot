import logging
import datetime
from pprint import pprint

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
    def show_charts(cls, symbol, interval, date_from=None, date_to=None):
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
        cls._calc_buy_sell(df)
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
        )
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(candlestick)
        fig.add_trace(ema_scatter, secondary_y=True)
        fig.add_trace(buy_sell_scatter, secondary_y=True)
        fig['layout'].update(title='EMA Chart', xaxis=dict(tickangle=-90))
        plot(fig)

    @staticmethod
    def _calc_buy_sell(df):
        lowest = None
        highest = None
        df['bs'] = np.NaN
        last_buy = 0
        last_sell = 0
        operations = {
            'buys': 0,
            'sells': 0,
            'long_profit': 0,
            'short_profit': 0,
        }
        for i, row in df.iterrows():
            row['close'] = float(row['close'])
            row['ema'] = float(row['ema'])
            if lowest is None and highest is None:
                lowest = row
                highest = row
                continue
            if (
                (row['ema'] - lowest['ema'])
                > (lowest['ema'] * constants.CONFIG_EMA_DROP_PERCENT)
            ):
                df.at[i, 'bs'] = row['close']
                operations['buys'] += 1
                last_buy = row['close']
                if last_sell:
                    operations['short_profit'] += last_sell - row['close']
            if (
                (highest['ema'] - row['ema'])
                > (highest['ema'] * constants.CONFIG_EMA_DROP_PERCENT)
            ):
                df.at[i, 'bs'] = row['close']
                operations['sells'] += 1
                last_sell = row['close']
                if last_buy:
                    operations['long_profit'] += row['close'] - last_buy
            if (row['ema'] - highest['ema']) > 0:
                highest = row
            if (row['ema'] - lowest['ema']) < 0:
                lowest = row
        pprint(operations)
