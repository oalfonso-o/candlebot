import math

from candlebot import utils
from candlebot.db.candle_retriever import CandleRetriever
from candlebot.strategist import Strategist
from candlebot import constants


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
    balance_origin = []
    balance_long = []
    balance_short = []
    chart_positions_long = []
    index_positions_long = 0
    ema10 = []
    ema20 = []
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

        candles.append(candle)
        any_marker_shown = False
        if (
            index_positions_long < len(wallet.positions_long)
            and (
                wallet.positions_long[index_positions_long].timestamp
                / 1000 == time
            )
        ):
            add_open_close_points_to_chart_positions(
                wallet.positions_long[index_positions_long],
                balance_origin,
                balance_long,
                balance_short,
                time,
                chart_positions_long,
            )
            index_positions_long += 1
            any_marker_shown = True
        else:
            chart_positions_long.append({'time': time})
        if not any_marker_shown:
            balance_origin.append({'time': time})
            balance_long.append({'time': time})
            balance_short.append({'time': time})
    return [
        {
            'id': 'open/close long positions',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_long,
                },
                {'type': 'lines', 'values': ema10, 'color': '#008000'},
                {'type': 'lines', 'values': ema20, 'color': '#0000FF'},
            ],
            'width': 1200,
            'height': 500,
        },
        {
            'id': 'balance_origin',
            'series': [
                {'type': 'lines', 'values': balance_origin, 'color': '#39f'},
            ],
            'width': 1200,
            'height': 100,
        },
        {
            'id': 'balance_long',
            'series': [
                {'type': 'lines', 'values': balance_long, 'color': '#f5a'},
            ],
            'width': 1200,
            'height': 100,
        },
    ]


def add_open_close_points_to_chart_positions(
    position, balance_origin, balance_long, balance_short, time,
    chart_positions
):
    point_balance_origin = {'time': time, 'value': position.balance_origin}
    point_balance_long = {'time': time, 'value': position.balance_long}
    point_balance_short = {'time': time, 'value': position.balance_short}
    balance_origin.append(point_balance_origin)
    balance_long.append(point_balance_long)
    balance_short.append(point_balance_short)
    if position.action == 'open':
        point_open_position = {
            'time': time,
            'text': str(round(position.amount, 4)),
            'position': 'belowBar',
            'color': 'blue',
            'shape': 'arrowUp',
        }
        chart_positions.append(point_open_position)
    if position.action == 'close':
        point_close_position = {
            'time': time,
            'text': str(round(position.amount, 4)),
            'position': 'aboveBar',
            'color': 'green',
            'shape': 'arrowDown',
        }
        chart_positions.append(point_close_position)
