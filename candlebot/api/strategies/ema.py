import datetime

from candlebot import utils
from candlebot.db.candle_retriever import CandleRetriever
from candlebot.strategist import Strategist
from candlebot import constants


def calc():
    now = datetime.datetime.now()
    two_ago = datetime.datetime.now() - datetime.timedelta(days=356 * 2)
    candles_cursor = CandleRetriever.get(
        'ETHUSDT',
        '1d',
        utils.datetime_to_timestamp(two_ago),
        utils.datetime_to_timestamp(now),
    )
    candles = list(candles_cursor)
    strat_df, wallet = Strategist.calc(candles, 'ema')
    candles = []
    ema = []
    balance_origin = []
    balance_long = []
    balance_short = []
    chart_positions_long = []
    chart_positions_short = []
    index_positions_long = 0
    index_positions_short = 0
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
        ema_line = {'time': time, 'value': c['ema']}
        candles.append(candle)
        ema.append(ema_line)
        any_marker_shown = False
        if (
            index_positions_long < len(wallet.positions_long)
            and (
                wallet.positions_long[index_positions_long].timestamp
                / 1000 == time
            )
        ):
            add_points_to_chart_positions(
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
        if (
            index_positions_short < len(wallet.positions_short)
            and (
                wallet.positions_short[index_positions_short].timestamp
                / 1000 == time
            )
        ):
            add_points_to_chart_positions(
                wallet.positions_short[index_positions_short],
                balance_origin,
                balance_long,
                balance_short,
                time,
                chart_positions_short,
            )
            index_positions_short += 1
            any_marker_shown = True
        else:
            chart_positions_short.append({'time': time})
        if not any_marker_shown:
            balance_origin.append({'time': time})
            balance_long.append({'time': time})
            balance_short.append({'time': time})

    return [
        {
            'id': 'open/close long',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_long,
                },
                {
                    'type': 'lines',
                    'values': ema,
                    'color': '#999',
                    'lineType': 1,
                },
            ],
            'width': 800,
            'height': 250,
        },
        {
            'id': 'open/close short',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_short,
                },
                {
                    'type': 'lines',
                    'values': ema,
                    'color': '#999',
                    'lineType': 1,
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
        {
            'id': 'balance_short',
            'series': [
                {'type': 'lines', 'values': balance_short, 'color': '#941'},
            ],
            'width': 800,
            'height': 100,
        },
    ]


def add_points_to_chart_positions(
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
