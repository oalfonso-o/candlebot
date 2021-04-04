import logging

from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from crypto.db import db_find
from crypto import constants
from crypto import utils
from crypto import settings

logger = logging.getLogger(__name__)


class Charter:

    def __init__(
        self,
        window=settings.BT_CONFIG['ema']['window'],
        adjust=settings.BT_CONFIG['ema']['adjust'],
        drop_factor=settings.BT_CONFIG['ema']['drop_factor'],
    ):
        self.window = window
        self.adjust = adjust
        self.drop_factor = drop_factor

    def calc_chart(
        self, symbol, interval, date_from=None, date_to=None, show_plot=True
    ):
        logger.info(f'Charting {symbol}_{interval} f:{date_from} t:{date_to}')
        query = {}
        if date_from or date_to:
            query = {'_id': {}}
            if date_from:
                query['_id']['$gte'] = int(date_from)
            if date_to:
                query['_id']['$lte'] = int(date_to)
        all_cursor = db_find.find(
            symbol, interval, query, constants.KLINE_FIELDS)
        docs = list(all_cursor)
        if not docs:
            logging.warning('No klines')
            return {}
        df = pd.DataFrame(docs)
        df['_id'] = df['_id'].apply(lambda _id: utils.timestamp_to_date(_id))
        df['ema'] = df['close'].ewm(
            span=self.window, adjust=self.adjust
        ).mean()
        operations = self._calc_buy_sell(df)
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

    def _calc_buy_sell(self, df):
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
            'long_profit_percents': [],
            'short_profit_percents': [],
        }
        for i, row in df.iterrows():
            row['close'] = float(row['close'])
            row['ema'] = float(row['ema'])
            row['bs'] = float(0)
            if lowest is None and highest is None:
                lowest = row
                highest = row
                continue
            if self._must_buy(row, lowest, direction):
                df.at[i, 'bs'] = row['close']
                operations['buys'] += 1
                last_buy = row['close']
                if last_sell:
                    profit = last_sell - row['close']
                    operations['short_profit'] += profit
                    percent_profit = profit / last_sell
                    operations['short_profit_percents'].append(percent_profit)
                direction = 1
            elif self._must_sell(row, highest, direction):
                df.at[i, 'bs'] = row['close']
                operations['sells'] += 1
                last_sell = row['close']
                if last_buy:
                    profit = row['close'] - last_buy
                    operations['long_profit'] += profit
                    percent_profit = profit / last_buy
                    operations['long_profit_percents'].append(percent_profit)
                direction = -1
            if (row['ema'] - highest['ema']) > 0:
                highest = row
            if (row['ema'] - lowest['ema']) < 0:
                lowest = row
        return operations

    def _must_buy(self, row, lowest, direction):
        return bool(
            (row['ema'] - lowest['ema'])
            > (lowest['ema'] * self.drop_factor)
            and (not direction or direction < 0)
        )

    def _must_sell(self, row, highest, direction):
        return bool(
            (highest['ema'] - row['ema'])
            > (highest['ema'] * self.drop_factor)
            and (not direction or direction > 0)
        )
