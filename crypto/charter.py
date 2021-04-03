import datetime
import logging

import plotly.graph_objects as go
import pandas as pd

from crypto.db import db_find

logger = logging.getLogger(__name__)


class Charter:

    @staticmethod
    def show_charts(symbol):
        logger.info(f'Trading {symbol}')
        fields = {'open': 1, 'high': 1, 'low': 1, 'close': 1}
        date_from = datetime.datetime.now() - datetime.timedelta(days=2)
        query = {'_id': {'$gte': date_from.timestamp() * 1000}}
        all_cursor = db_find.find(symbol, query, fields)
        df = pd.DataFrame(list(all_cursor))
        figure = go.Figure(
            data=[
                go.Candlestick(
                    x=df['_id'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close']
                )
            ]
        )
        figure.show()
