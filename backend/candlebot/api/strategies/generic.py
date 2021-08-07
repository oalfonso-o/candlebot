import logging
import random
from collections import defaultdict

from candlebot import utils
from candlebot import constants
from candlebot.db.candle_retriever import CandleRetriever
from candlebot.strategist import Strategist
from candlebot.api.strategies.utils import (
    add_open_close_points_to_chart_positions,
    basic_charts_dict,
)

logger = logging.getLogger(__name__)

colors = [
    'aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon',
    'navy', 'olive', 'orange', 'purple', 'red', 'silver', 'teal', 'white',
    'yellow'
]


def calc(
    strategy, date_from=None, date_to=None, symbol='ADAEUR', interval='1d'
):
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
    strat_df, wallet = Strategist.calc(candles, strategy)
    log_wallet_stats(wallet)
    Strategy = Strategist.all_strats()[strategy]
    candles = []
    chart_positions_long = []
    index_positions_long = 0
    lines_indicators = Strategy.indicators
    # markers_indicators = Strategy.markers_indicators
    lines_series_data = defaultdict(list)
    # markers_series_data = []
    for _, c in strat_df.iterrows():
        time = get_time(c)
        candle = get_candle_dict(candle=c, time=time)
        candles.append(candle)
        index_positions_long = add_long_markers(
            index_positions_long=index_positions_long,
            wallet=wallet,
            time=time,
            chart_positions_long=chart_positions_long,
        )
        add_lines_series_data_points(
            indicators=lines_indicators,
            lines_series_data=lines_series_data,
            time=time,
            candle=c,
        )

    lines_series = get_lines_series(lines_series_data)
    charts = basic_charts_dict(candles, chart_positions_long, lines_series)
    return charts


def get_time(candle):
    return (
        utils.datetime_to_timestamp(candle['_id'].to_pydatetime())
        / constants.DATE_MILIS_PRODUCT
    )


def get_candle_dict(candle, time):
    return {
        'time': time,
        'open': candle['open'],
        'close': candle['close'],
        'high': candle['high'],
        'low': candle['low'],
        'volume': candle['volume'],
    }


def log_wallet_stats(wallet):  # TODO: return to frontend and print in a div
    logger.info(f'wins: {wallet.stats.wins}')
    logger.info(f'losses: {wallet.stats.losses}')
    logger.info(f'win/lose: {wallet.stats.win_lose_ratio}')
    logger.info(f'final balance: {wallet.stats.balance}')
    logger.info(f'% earn: {wallet.stats.earn_percentage}%')


def add_long_markers(index_positions_long, wallet, time, chart_positions_long):
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
    return index_positions_long


def add_lines_series_data_points(indicators, lines_series_data, time, candle):
    for i in indicators:
        point = {'time': time, 'value': candle[i._id]}
        lines_series_data[i._id].append(point)


def get_lines_series(lines_series_data):
    series = []
    for id_, data in lines_series_data.items():
        serie = {
            'title': id_,
            'values': data,
            'color': random.choice(colors),
            'type': 'lines',
        }
        series.append(serie)
    return series
