import logging
import datetime

from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.graph_objects as go
import pandas as pd

from crypto.db import db_find
from crypto import constants

logger = logging.getLogger(__name__)


class Charter:

    @staticmethod
    def show_charts(symbol, interval, date_from=None, date_to=None):
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
        df['ema_short'] = df['close'].ewm(span=20, adjust=False).mean()
        candlestick = go.Candlestick(
            x=df['_id'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
        )
        ema_scatter = go.Scatter(
            x=df['_id'],
            y=df['ema_short'],
            name='EMA 20',
            yaxis='y2',
        )
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(candlestick)
        fig.add_trace(ema_scatter, secondary_y=True)
        fig['layout'].update(
            height=600, width=800, title='EMA Chart', xaxis=dict(tickangle=-90)
        )
        plot(fig)
