import math

from candlebot import utils
from candlebot.db.candle_retriever import CandleRetriever
from candlebot.strategist import Strategist
from candlebot import constants


def calc(date_from=None, date_to=None, symbol='ADAUSDT', interval='1h'):
    if date_from and date_to:
        date_from_no_hyphen = date_from.replace('-', '')
        date_to_no_hyphen = date_to.replace('-', '')
        date_from = utils.date_to_timestamp(date_from_no_hyphen)
        date_to = utils.date_to_timestamp(date_to_no_hyphen)
    candles_cursor = CandleRetriever.get(
        symbol,
        interval,
        date_from,
        date_to,
    )
    candles = list(candles_cursor)
    if not candles:
        return []
    strat_df, wallet = Strategist.calc(candles, 'triangle')
    candles = []
    chart_positions_long = []
    ma200 = []
    ma50 = []
    ma20 = []
    for _, c in strat_df.iterrows():
        time = (
            utils.datetime_to_timestamp(c['_id'].to_pydatetime())
            / constants.DATE_MILIS_PRODUCT
        )
        candle = {
            'time': time,
            'open': c['open'],
            'close': c['close'],
            'high': c['high'],
            'low': c['low'],
            'volume': c['volume'],
        }
        candles.append(candle)
        candles.append(candle)
        ma200_value = 0 if math.isnan(c['ma200']) else c['ma200']
        ma200_line = {'time': time, 'value': ma200_value}
        ma200.append(ma200_line)
        ma50_value = 0 if math.isnan(c['ma50']) else c['ma50']
        ma50_line = {'time': time, 'value': ma50_value}
        ma50.append(ma50_line)
        ma20_value = 0 if math.isnan(c['ma20']) else c['ma20']
        ma20_line = {'time': time, 'value': ma20_value}
        ma20.append(ma20_line)
    return [
        {
            'id': 'open/close long positions',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_long,
                },
                {
                    'type': 'lines',
                    'values': ma200,
                    'color': '#fff200',
                    'lineType': 1,
                },
                {
                    'type': 'lines',
                    'values': ma50,
                    'color': '#00ffaa',
                    'lineType': 1,
                },
                {
                    'type': 'lines',
                    'values': ma20,
                    'color': '#ee00ff',
                    'lineType': 1,
                },
            ],
            'width': 800,
            'height': 250,
        },
    ]
