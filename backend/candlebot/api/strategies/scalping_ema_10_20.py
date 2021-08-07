import math

from candlebot import utils
from candlebot import constants
from candlebot.strategist import Strategist
from candlebot.db.candle_retriever import CandleRetriever
from candlebot.api.strategies.utils import (
    add_open_close_points_to_chart_positions,
)


def calc(date_from=None, date_to=None, symbol='ADAEUR', interval='1d'):
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
    strat_df, wallet = Strategist.calc(candles, 'scalping_ema_10_20')
    candles = []
    chart_positions_long = []
    index_positions_long = 0
    ema10 = []
    ema20 = []
    zigzag = []
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
        ema10_line = {'time': time, 'value': c['ema10'] if not math.isnan(c['ema10']) else 300}  # noqa
        ema20_line = {'time': time, 'value': c['ema20'] if not math.isnan(c['ema20']) else 300}  # noqa
        ema10.append(ema10_line)
        ema20.append(ema20_line)
        zigzag_line = {'time': time}
        if c['zigzag']:
            zigzag_line['value'] = c['zigzag']
        zigzag.append(zigzag_line)

        candles.append(candle)
        if (
            index_positions_long < len(wallet.positions_long)
            and (
                wallet.positions_long[index_positions_long].timestamp
                / 1000 == time
            )
        ):
            add_open_close_points_to_chart_positions(
                wallet.positions_long[index_positions_long],
                time,
                chart_positions_long,
            )
            index_positions_long += 1
        else:
            chart_positions_long.append({'time': time})
    charts = [
        {
            'id': 'open/close long positions',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_long,
                },
                {'type': 'lines', 'values': zigzag, 'color': '#000', 'lineWidth': 3},  # noqa
                {'type': 'lines', 'values': ema10, 'color': '#008000'},
                {'type': 'lines', 'values': ema20, 'color': '#0000FF'},
            ],
            'width': 1200,
            'height': 500,
        },
    ]
    stats = {}
    return {
        'charts': charts,
        'stats': stats,
    }
