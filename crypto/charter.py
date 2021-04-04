import logging
import datetime

import plotly.graph_objects as go
import pandas as pd

from crypto.db import db_find

logger = logging.getLogger(__name__)


class Charter:

    @staticmethod
    def show_charts(symbol, interval, date_from=None, date_to=None):
        logger.info(f'Trading {symbol}')
        fields = {'open': 1, 'high': 1, 'low': 1, 'close': 1}
        query = {}
        if date_from or date_to:
            query = {'_id': {}}
            if date_from:
                query['_id']['$gte'] = int(date_from)
            if date_to:
                query['_id']['$lte'] = int(date_to)
        all_cursor = db_find.find(symbol, interval, query, fields)
        df = pd.DataFrame(list(all_cursor))
        df['_id'] = df['_id'].apply(
            lambda _id: datetime.datetime.fromtimestamp(_id / 1000)
        )
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
