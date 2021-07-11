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
    strat_df, wallet = Strategist.calc(candles, 'scalping')
    candles = []
    balance_origin = []
    balance_long = []
    balance_short = []
    chart_positions_long = []
    chart_positions_engulfing = []
    index_positions_long = 0
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
        if not math.isnan(c['engulfing']):
            add_engulfing_points_to_chart(
                time, c['engulfing'], chart_positions_engulfing
            )
        else:
            chart_positions_engulfing.append({'time': time})
    return [
        {
            'id': 'open/close long positions',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_long,
                },
            ],
            'width': 800,
            'height': 250,
        },
        {
            'id': 'Engulfing marks',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_engulfing,
                },
            ],
            'width': 800,
            'height': 250,
        },
        {
            'id': 'balance_origin',
            'series': [
                {'type': 'lines', 'values': balance_origin, 'color': '#39f'},
            ],
            'width': 800,
            'height': 100,
        },
        {
            'id': 'balance_long',
            'series': [
                {'type': 'lines', 'values': balance_long, 'color': '#f5a'},
            ],
            'width': 800,
            'height': 100,
        },
    ]


def add_open_close_points_to_chart_positions(
    position, balance_origin, balance_long, balance_short, time,
    chart_positions
):
    point_balance_origin = {'time': time, 'value': position.balance_origin}  # noqa
    point_balance_long = {'time': time, 'value': position.balance_long}  # noqa
    point_balance_short = {'time': time, 'value': position.balance_short}  # noqa
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


def add_engulfing_points_to_chart(time, value, chart_positions_engulfing):
    if value > 0:
        text = 'buy'
        position = 'belowBar'
        color = 'green'
        shape = 'arrowUp'
    else:
        text = 'sell'
        position = 'aboveBar'
        color = 'red'
        shape = 'arrowDown'
    point_open_position = {
        'time': time,
        'text': text,
        'position': position,
        'color': color,
        'shape': shape,
    }
    chart_positions_engulfing.append(point_open_position)
