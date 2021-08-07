from collections import defaultdict
import math

from candlebot import utils
from candlebot.db.candle_retriever import CandleRetriever
from candlebot.strategies.triangle import StrategyTriangle
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
    strat_df, _ = Strategist.calc(candles, 'triangle')
    candles = []
    ma200 = []
    ma50 = []
    ma20 = []
    highs = []
    lows = []
    projections = defaultdict(list)
    latest_projection_time = None
    for _, c in strat_df.iterrows():
        time = (
            utils.datetime_to_timestamp(c['_id'].to_pydatetime())
            / constants.DATE_MILIS_PRODUCT
        )
        if not latest_projection_time:
            latest_projection_time = time
        if not math.isnan(c['close']):
            candle = {
                'time': time,
                'open': c['open'],
                'close': c['close'],
                'high': c['high'],
                'low': c['low'],
                'volume': c['volume'],
            }
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
        if not math.isnan(c['day_highest']):
            highs.append({'time': time, 'value': c['day_highest']})
        if not math.isnan(c['day_lowest']):
            lows.append({'time': time, 'value': c['day_lowest']})

        for i in range(1, StrategyTriangle.BACK_CHECK_POSITIONS+1):
            if not math.isnan(c[f'high_projection_{i}']):
                projections[f'high_projection_{i}'].append(
                    {'time': time, 'value': c[f'high_projection_{i}']})
                if time > latest_projection_time:
                    latest_projection_time = time
    # TODO: fill projection hours
    # last_day_until_last_projection_day = 5
    # for day in last_day_until_last_projection_day:
    #     latest_projection_time
    projection_lines = [
        {
            'type': 'lines',
            'values': values,
            'color': '#ff00ee',
            'lineType': 2,
            'lineWidth': 1,
        }
        for values in projections.values()
    ]
    charts = [
        {
            'id': 'open/close long positions',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                },
                {
                    'type': 'lines',
                    'values': ma200,
                    'color': '#fff200',
                    'lineType': 2,
                },
                {
                    'type': 'lines',
                    'values': ma50,
                    'color': '#00ffaa',
                    'lineType': 2,
                },
                {
                    'type': 'lines',
                    'values': ma20,
                    'color': '#ee00ff',
                    'lineType': 2,
                },
                {
                    'type': 'lines',
                    'values': highs,
                    'color': '#00ff00',
                    'lineType': 2,
                    'lineWidth': 3,
                },
                {
                    'type': 'lines',
                    'values': lows,
                    'color': '#ff0000',
                    'lineType': 2,
                    'lineWidth': 3,
                },
                *projection_lines,
            ],
            'width': 1400,
            'height': 650,
        },
    ]
    stats = {}
    return {
        'charts': charts,
        'stats': stats,
    }
