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
    chart_positions_fractals = []
    chart_positions_engulfing = []
    index_positions_long = 0
    smma21 = []
    smma50 = []
    smma200 = []
    stochk = []
    stochd = []
    stoch_top = []
    stoch_bottom = []
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
        smma21_line = {'time': time, 'value': c['smma21'] if not math.isnan(c['smma21']) else 300}  # noqa
        smma50_line = {'time': time, 'value': c['smma50'] if not math.isnan(c['smma50']) else 300}  # noqa
        smma200_line = {'time': time, 'value': c['smma200'] if not math.isnan(c['smma200']) else 300}  # noqa
        smma21.append(smma21_line)
        smma50.append(smma50_line)
        smma200.append(smma200_line)
        stochk_line = {'time': time, 'value': c['stoch_rsi_k'] if not math.isnan(c['stoch_rsi_k']) else 300}  # noqa
        stochd_line = {'time': time, 'value': c['stoch_rsi_d'] if not math.isnan(c['stoch_rsi_d']) else 300}  # noqa
        stoch_top_line = {'time': time, 'value': 0.8}
        stoch_bottom_line = {'time': time, 'value': 0.2}
        stochk.append(stochk_line)
        stochd.append(stochd_line)
        stoch_top.append(stoch_top_line)
        stoch_bottom.append(stoch_bottom_line)

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
        if c['william_bull_fractals']:
            add_fractals_points_to_chart(
                time, 'bull', chart_positions_fractals
            )
        elif c['william_bear_fractals']:
            add_fractals_points_to_chart(
                time, 'bear', chart_positions_fractals
            )
        else:
            chart_positions_fractals.append({'time': time})
        if c['engulfing']:
            point_engulfing_position = {
                'time': time,
                'text': 'bull',
                'position': 'belowBar',
                'color': 'blue',
                'shape': 'arrowUp',
            }
        else:
            point_engulfing_position = {'time': time}
        chart_positions_engulfing.append(point_engulfing_position)
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
            'width': 1200,
            'height': 250,
        },
        {
            'id': 'Fractal marks',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_fractals,
                },
                {'type': 'lines', 'values': smma21, 'color': '#008000'},
                {'type': 'lines', 'values': smma50, 'color': '#0000FF'},
                {'type': 'lines', 'values': smma200, 'color': '#FF0000'},
            ],
            'width': 1200,
            'height': 250,
        },
        {
            'id': 'Stoch RSI',
            'series': [
                {'type': 'lines', 'values': stochk, 'color': '#290af5'},
                {'type': 'lines', 'values': stochd, 'color': '#fcba03'},
                {'type': 'lines', 'values': stoch_top, 'color': '#f50a0a'},
                {'type': 'lines', 'values': stoch_bottom, 'color': '#f50a0a'},
            ],
            'width': 1200,
            'height': 250,
        },
        # {
        #     'id': 'Engulfing marks',
        #     'series': [
        #         {
        #             'type': 'candles',
        #             'values': candles,
        #             'markers': chart_positions_engulfing,
        #         },
        #         {'type': 'lines', 'values': smma21, 'color': '#008000'},
        #         {'type': 'lines', 'values': smma50, 'color': '#0000FF'},
        #         {'type': 'lines', 'values': smma200, 'color': '#FF0000'},
        #     ],
        #     'width': 1200,
        #     'height': 300,
        # },
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


def add_fractals_points_to_chart(time, value, chart_positions_fractals):
    if value == 'bull':
        text = 'bull'
        position = 'belowBar'
        color = 'red'
        shape = 'arrowDown'
    elif value == 'bear':
        text = 'bear'
        position = 'aboveBar'
        color = 'green'
        shape = 'arrowUp'
    point_open_position = {
        'time': time,
        'text': text,
        'position': position,
        'color': color,
        'shape': shape,
    }
    chart_positions_fractals.append(point_open_position)
